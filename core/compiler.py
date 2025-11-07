import shutil
import tempfile
import os
import subprocess
import asyncio
import urllib.request
import re
import uuid
import serial.tools.list_ports
import webview
import sys
import sqlite3
from pathlib import Path
from core.utils import get_bundled_python_exe
from core.db import db_path as DB_PATH

from core.serial_manager import get_valid_serial_port

from core.transpiler.transpiler import main as transpiler_main

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CORE_LIBS_PATH = os.path.join(BASE_DIR, "transpiler", "core_libs")

# Global state to track installation
_PLATFORMIO_INSTALLED = False


def _get_relevant_platform_version(platform):
    if platform == "espressif32":
        return f"{platform}@6.5.0"
    return platform


def release_serial_port(port: str):
    """Ensure no lingering lock on the serial port."""
    try:
        with serial.Serial(port, baudrate=115200, timeout=1) as ser:
            print(f"🔌 Released serial port: {port}")
    except serial.SerialException as e:
        print(f"⚠️ Could not open {port} to release: {e}")


def find_first_serial_port():
    ports = list(serial.tools.list_ports.comports())
    if not ports:
        raise RuntimeError("❌ No serial ports found.")
    return ports[0].device


import serial
import serial.tools.list_ports
import time


def find_esp_serial_port(preferred_baud=115200, probe=True, timeout=1.5):
    """
    Auto-detect any ESP device connected via serial (ESP32/ESP8266/ESP32-S3/C3 etc).

    Strategy:
      1. Scan all available serial ports.
      2. Match known Espressif and USB-to-UART bridge VIDs/PIDs.
      3. If no direct match, try to probe each port for ESP bootloader banner.
      4. Return the first port that looks like an ESP device.

    Returns:
      str: The serial port name (e.g., 'COM6' or '/dev/ttyUSB0'), or None if not found.
    """

    # Known USB vendor IDs for ESP and bridges
    known_vids = {
        0x303A: "Espressif",
        0x10C4: "Silicon Labs (CP210x)",
        0x1A86: "QinHeng (CH340)",
        0x0403: "FTDI",
        0x2341: "Arduino (may host ESP chips)",
        0x2E8A: "Raspberry Pi (RP2040 boards with ESP co-modules)",
    }

    ports = list(serial.tools.list_ports.comports())
    if not ports:
        print("❌ No serial ports found.")
        return None

    print("🔍 Scanning available serial ports...")
    for p in ports:
        desc = f"{p.description or ''}".lower()
        vid = getattr(p, "vid", None)
        pid = getattr(p, "pid", None)
        print(f"   - {p.device}: VID={vid}, PID={pid}, Desc={desc}")

        # --- Step 1: Match known VIDs or descriptions ---
        if vid in known_vids or any(
            word in desc
            for word in [
                "esp32",
                "esp8266",
                "espressif",
                "silicon labs",
                "ch340",
                "cp210",
                "usb serial",
                "ftdi",
            ]
        ):
            print(
                f"✅ Candidate ESP device detected on {p.device} ({known_vids.get(vid, desc)})"
            )
            return p.device

    # --- Step 2: Probe all ports if nothing matched ---
    if probe:
        print(
            "🧪 No direct match found; probing each port for ESP bootloader response..."
        )
        for p in ports:
            try:
                with serial.Serial(p.device, preferred_baud, timeout=timeout) as ser:
                    ser.reset_input_buffer()
                    ser.write(b"\r\n")
                    time.sleep(0.3)
                    data = ser.read(128).decode(errors="ignore").lower()
                    if any(
                        keyword in data
                        for keyword in ["esp32", "esp8266", "espressif", "rst:"]
                    ):
                        print(f"✅ ESP bootloader detected on {p.device}")
                        return p.device
            except Exception as e:
                print(f"⚠️ Skipping {p.device}: {e}")

    print("❌ No ESP device detected.")
    return None


def is_platformio_installed(target_dir: str) -> bool:
    for item in os.listdir(target_dir):
        if item.startswith("platformio") and (
            item.endswith(".dist-info") or os.path.isdir(os.path.join(target_dir, item))
        ):
            return True
    return False


async def stream_command_to_terminal(cmd, cwd=None, env=None):
    """
    Run a subprocess command, stream its output to terminal + frontend,
    and also collect logs for later parsing.
    Returns (stdout_str, stderr_str, exit_code).
    """
    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        cwd=cwd,
        env=env,
    )

    stdout_data, stderr_data = [], []

    async def stream_output(stream, collector):
        while True:
            line = await stream.readline()
            if not line:
                break
            decoded = line.decode(errors="ignore").rstrip()
            collector.append(decoded)

            # ✅ Print to local terminal
            print(decoded)

            # ✅ Send to frontend terminal
            try:
                webview.windows[0].evaluate_js(
                    f"window.__appendTerminalLog({decoded!r})"
                )
            except Exception as e:
                print(f"[TerminalLog] JS error: {e}")

    await asyncio.gather(
        stream_output(process.stdout, stdout_data),
        stream_output(process.stderr, stderr_data),
    )

    code = await process.wait()
    return "\n".join(stdout_data), "\n".join(stderr_data), code


def ensure_pip_and_install_pio(python_exe: str, target_dir: str):
    print(f"🧪 Checking for pip in: {python_exe}")

    def has_pip():
        try:
            subprocess.run(
                [python_exe, "-m", "pip", "--version"], check=True, capture_output=True
            )
            return True
        except subprocess.CalledProcessError:
            return False

    if not has_pip():
        print("⚠️ pip not found. Trying to install with ensurepip...")
        try:
            subprocess.run([python_exe, "-m", "ensurepip", "--upgrade"], check=True)
            print("✅ pip installed using ensurepip.")
        except Exception as e:
            print("❌ ensurepip failed:", e)
            print("📥 Downloading get-pip.py as fallback...")
            with urllib.request.urlopen("https://bootstrap.pypa.io/get-pip.py") as resp:
                code = resp.read()
            with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as tmpfile:
                tmpfile.write(code)
                tmpfile_path = tmpfile.name
            subprocess.run([python_exe, tmpfile_path], check=True)
            print("✅ pip installed using get-pip.py")

    if not is_platformio_installed(target_dir):
        print("📦 Installing PlatformIO into:", target_dir)
        subprocess.run(
            [
                python_exe,
                "-m",
                "pip",
                "install",
                "--upgrade",
                "--target",
                target_dir,
                "platformio",
            ],
            check=True,
        )
        print("✅ PlatformIO installation complete.")
    else:
        print("🟢 PlatformIO already installed. Skipping pip install.")


def parse_platformio_result(stdout: str, stderr: str) -> dict:
    # Combine all output for analysis
    all_output = stdout + "\n" + stderr

    # DEBUG: Print what we're analyzing
    print(f"🔍 Analyzing output for success/failure...")
    print(f"🔍 stdout contains [SUCCESS]: {'[SUCCESS]' in stdout}")
    print(f"🔍 stdout contains [FAILED]: {'[FAILED]' in stdout}")
    print(f"🔍 stderr contains error: {'error:' in stderr.lower()}")
    print(
        f"🔍 all_output contains compilation error: {any(word in all_output.lower() for word in ['error:', '*** [', 'failed'])}"
    )

    # Check for the most obvious failure markers FIRST
    has_failed_marker = "[FAILED]" in stdout
    has_success_marker = "[SUCCESS]" in stdout

    # Check for compiler/linker errors
    has_compiler_error = any(
        pattern in all_output
        for pattern in ["error:", "*** [", "does not name a type", "Error 1"]
    )

    # Check for specific error patterns that indicate failure
    has_specific_errors = any(
        error_pattern in all_output
        for error_pattern in [
            "does not name a type",
            "expected",
            "undefined reference",
            "compilation terminated",
            "No such file or directory",
        ]
    )

    # If we have ANY failure markers or errors, compilation failed
    # If we have success marker AND no failure indicators, compilation succeeded
    compilation_failed = has_failed_marker or has_compiler_error or has_specific_errors
    compilation_succeeded = has_success_marker and not compilation_failed

    print(
        f"🔍 Final determination: failed={compilation_failed}, succeeded={compilation_succeeded}"
    )

    result = {
        "success": compilation_succeeded,
        "message": "Compilation successful"
        if compilation_succeeded
        else "Compilation failed",
        "specs": {
            "flash": {"used": 0, "total": 0},
            "ram": {"used": 0, "total": 0},
            "additional": {},
        },
        "warnings": [],
        "suggestions": [],
        "errors": [],
    }

    lines_out = stdout.splitlines()
    lines_err = stderr.splitlines()

    # Only parse memory usage if compilation was successful
    memory_parsed = False
    if compilation_succeeded:
        for line in lines_out:
            # Parse RAM usage
            if "RAM:" in line and "used" in line and "bytes from" in line:
                match = re.search(r"used\s+(\d+)\s+bytes\s+from\s+(\d+)", line)
                if match:
                    result["specs"]["ram"]["used"] = int(match.group(1))
                    result["specs"]["ram"]["total"] = int(match.group(2))
                    memory_parsed = True

            # Parse Flash usage
            elif "Flash:" in line and "used" in line and "bytes from" in line:
                match = re.search(r"used\s+(\d+)\s+bytes\s+from\s+(\d+)", line)
                if match:
                    result["specs"]["flash"]["used"] = int(match.group(1))
                    result["specs"]["flash"]["total"] = int(match.group(2))
                    memory_parsed = True

            # Parse firmware info
            elif "firmware.elf" in line and "Linking" in line:
                result["specs"]["additional"]["Firmware ELF"] = line.strip().split()[-1]
            elif "firmware.bin" in line and "Building" in line:
                result["specs"]["additional"]["Firmware BIN"] = line.strip().split()[-1]

            # Parse duration
            elif "Took" in line and "seconds" in line:
                match = re.search(r"Took ([\d.]+) seconds", line)
                if match:
                    result["specs"]["additional"]["Duration"] = f"{match.group(1)}s"

    # Collect ALL errors and warnings
    for line in lines_out + lines_err:
        line_lower = line.lower()
        if "error:" in line_lower:
            if line.strip() not in result["errors"]:
                result["errors"].append(line.strip())
        elif "warning:" in line_lower:
            if line.strip() not in result["warnings"]:
                result["warnings"].append(line.strip())

    # Specifically look for compilation error patterns
    for line in lines_out:
        if any(
            pattern in line for pattern in ["*** [", "Error 1", "does not name a type"]
        ):
            if line.strip() not in result["errors"]:
                result["errors"].append(line.strip())

    # Set the main error message if compilation failed
    if compilation_failed:
        if result["errors"]:
            # Use the first meaningful error as the main error
            for error in result["errors"]:
                if "error:" in error.lower():
                    result["error"] = error
                    break
            else:
                result["error"] = (
                    result["errors"][0] if result["errors"] else "Compilation failed"
                )
        else:
            result["error"] = "Compilation failed - check build output"

    # Generate helpful suggestions based on the errors
    if compilation_failed:
        all_errors_text = " ".join(result["errors"]).lower()

        if "does not name a type" in all_errors_text:
            result["suggestions"] = [
                "Check for undefined variables or functions",
                "Verify all variables are declared before use",
                "Check for missing #include statements",
            ]
        elif "undefined reference" in all_errors_text:
            result["suggestions"] = [
                "Check if all required libraries are included",
                "Verify function declarations match definitions",
                "Check library dependencies in platformio.ini",
            ]
        elif (
            "memory" in all_errors_text
            or "ram" in all_errors_text
            or "flash" in all_errors_text
        ):
            result["suggestions"] = [
                "Reduce global variable usage",
                "Use PROGMEM for constant data",
                "Optimize string usage with F() macro",
            ]
        else:
            result["suggestions"] = [
                "Check the compilation output for specific error details"
            ]

    print(
        f"🔍 Parse result: success={result['success']}, error={result.get('error', 'None')}"
    )
    return result


def install_platformio_once(user_app_dir: str):
    """
    Install PlatformIO once during app installation/setup.
    This should be called separately from your main application setup.
    """
    global _PLATFORMIO_INSTALLED

    if _PLATFORMIO_INSTALLED:
        print("🟢 PlatformIO already installed (cached).")
        return True

    pio_home = os.path.join(user_app_dir, ".platformio")
    python_exe = get_bundled_python_exe()

    print("🚀 Installing PlatformIO for first-time use...")
    print(f"🔍 Using Python: {python_exe}")
    print(f"🔍 PlatformIO home: {pio_home}")

    try:
        # Use virtual environment approach for better reliability
        venv_dir = os.path.join(pio_home, "platformio_venv")
        marker_file = Path(venv_dir) / ".pio_installed"

        if marker_file.exists():
            print("🟢 PlatformIO virtual environment already exists.")
            _PLATFORMIO_INSTALLED = True
            return True

        print(f"🔧 Creating virtual environment in: {venv_dir}")

        # Create virtual environment
        result = subprocess.run(
            [python_exe, "-m", "venv", venv_dir], capture_output=True, text=True
        )

        if result.returncode != 0:
            print(f"❌ Virtual environment creation failed: {result.stderr}")
            return False

        print("✅ Virtual environment created.")

        # Get venv Python executable
        if sys.platform == "win32":
            venv_python = os.path.join(venv_dir, "Scripts", "python.exe")
        else:
            venv_python = os.path.join(venv_dir, "bin", "python")

        # Wait a bit for venv to be fully ready
        import time

        time.sleep(2)

        # Install PlatformIO
        print("📦 Installing PlatformIO in virtual environment...")

        # Upgrade pip first
        pip_result = subprocess.run(
            [venv_python, "-m", "pip", "install", "--upgrade", "pip"],
            capture_output=True,
            text=True,
        )

        if pip_result.returncode != 0:
            print(f"⚠️ Pip upgrade had issues: {pip_result.stderr}")

        # Install PlatformIO
        pio_result = subprocess.run(
            [venv_python, "-m", "pip", "install", "platformio"],
            capture_output=True,
            text=True,
        )

        if pio_result.returncode != 0:
            print(f"❌ PlatformIO installation failed: {pio_result.stderr}")
            return False

        marker_file.write_text("installed")
        print("✅ PlatformIO installed successfully!")

        # Verify installation
        verify_result = subprocess.run(
            [
                venv_python,
                "-c",
                'import platformio; print(f"PlatformIO version: {platformio.__version__}")',
            ],
            capture_output=True,
            text=True,
        )

        if verify_result.returncode == 0:
            print(f"✅ {verify_result.stdout.strip()}")
        else:
            print(f"⚠️ Verification had issues: {verify_result.stderr}")

        _PLATFORMIO_INSTALLED = True
        return True

    except Exception as e:
        print(f"❌ Unexpected error during PlatformIO installation: {e}")
        return False


def get_platformio_command(user_app_dir: str):
    """
    Get the PlatformIO command and environment for compilation.
    This assumes PlatformIO is already installed via install_platformio_once().
    """
    pio_home = os.path.join(user_app_dir, ".platformio")
    venv_dir = os.path.join(pio_home, "platformio_venv")

    # Get the correct Python executable for the platform
    if sys.platform == "win32":
        venv_python = os.path.join(venv_dir, "Scripts", "python.exe")
    else:
        venv_python = os.path.join(venv_dir, "bin", "python")

    # Verify the virtual environment exists
    if not os.path.exists(venv_python):
        # Try to install it automatically
        print("🔄 PlatformIO not found, attempting automatic installation...")
        success = install_platformio_once(user_app_dir)
        if not success:
            raise FileNotFoundError(
                f"PlatformIO virtual environment not found at {venv_python} and "
                f"automatic installation failed. Please run install_platformio_once() first."
            )
        # After installation, verify again
        if not os.path.exists(venv_python):
            raise FileNotFoundError(
                f"PlatformIO virtual environment still not found at {venv_python} "
                f"after installation attempt."
            )

    env = os.environ.copy()
    env["PLATFORMIO_CORE_DIR"] = pio_home

    # Test that PlatformIO is accessible
    try:
        result = subprocess.run(
            [venv_python, "-c", "import platformio; print('PlatformIO available')"],
            capture_output=True,
            text=True,
            env=env,
        )
        if result.returncode != 0:
            print(f"⚠️ PlatformIO test had issues: {result.stderr}")
            # Don't raise here, let it try to run anyway
    except Exception as e:
        print(f"⚠️ PlatformIO verification had issues: {e}")
        # Don't raise here, let it try to run anyway

    return [
        venv_python,
        "-c",
        "import platformio.__main__; platformio.__main__.main()",
    ], env


def notify_frontend(status: str, message: str):
    """
    Send real-time build/upload status updates to the frontend.
    Your frontend should define:
        window.__updateBuildStatus = (phase, msg) => { ... }
    """
    try:
        js = f"window.__updateBuildStatus({status!r}, {message!r})"
        webview.windows[0].evaluate_js(js)
        print(f"[UI] {status}: {message}")
    except Exception as e:
        print(f"[UI Error] {e}")


async def compile_project(
    py_files: dict,
    board: str,
    platform: str,
    user_app_dir: str,
    upload: bool = False,
    port=None,
    dependencies=None,
):
    try:
        commit_hash = str(uuid.uuid4()).replace("-", "_")
        DB_CONN = sqlite3.connect(DB_PATH)

        notify_frontend("start", "Starting transpilation...")
        transpiler = transpiler_main(
            commit_hash, DB_CONN, py_files, CORE_LIBS_PATH, platform
        )
        notify_frontend("transpile_done", "Transpilation complete.")

        files = transpiler["code"]
        for filename, code in files.items():
            print(f"\n{'='*40}\n📄 {filename}\n{'='*40}")
            print(code.strip())
            print("\n")

        dependencies = transpiler["dependencies"]
        print("📦 Starting compilation...")

        notify_frontend("setup", "Preparing build environment...")
        pio_cmd, pio_env = get_platformio_command(user_app_dir)
        build_dir = prepare_build_folder()
        print(f"📁 Build folder prepared: {build_dir}")
        write_transpiled_code(files, build_dir)
        print("✍️ Transpiled files written.")
        write_platformio_ini(board, platform, build_dir, dependencies=dependencies)
        print(f"📝 platformio.ini written for board '{board}'.")
        notify_frontend("setup_done", "Build environment ready.")

        # Merge environments
        env = os.environ.copy()
        env.update(pio_env)

        print(f"🚀 Running PlatformIO compile in: {build_dir}")
        print(f"🔍 Command: {' '.join(pio_cmd)}")
        print(f"🔍 Working Directory: {build_dir}")

        notify_frontend("compile", "Compiling firmware...")
        stdout, stderr, code = await stream_command_to_terminal(
            pio_cmd + ["run"], cwd=build_dir, env=env
        )
        notify_frontend("compile_done", "Compilation complete.")

        parsed = parse_platformio_result(stdout, stderr)
        print(f"🔍 Parse result - success: {parsed['success']}, return code: {code}")

        # Add board info to specs
        if "specs" in parsed:
            parsed["specs"]["additional"]["Board"] = board
            parsed["specs"]["additional"]["Platform"] = platform

        # --- Upload phase with BOOT notification ---
        if upload and parsed["success"]:
            actual_port = port or find_esp_serial_port()
            if actual_port:
                print(f"🧭 Selected serial port: {actual_port}")
                release_serial_port(actual_port)
                await asyncio.sleep(1)

                # ✅ Ask user to press BOOT button (upload hasn't started yet)
                notify_frontend(
                    "press_boot",
                    "Hold the BOOT button on your ESP32 now and keep it pressed...",
                )
                await asyncio.sleep(3)  # Give user time to press BOOT

                # Create an event to track when upload actually starts
                upload_started = asyncio.Event()

                async def monitor_upload_output(stream, collector, upload_started):
                    """Monitor output and detect when upload actually begins"""
                    while True:
                        line = await stream.readline()
                        if not line:
                            break
                        decoded = line.decode(errors="ignore").rstrip()
                        collector.append(decoded)

                        # ✅ Print to local terminal
                        print(decoded)

                        # ✅ Detect upload start by looking for progress indicators
                        if not upload_started.is_set():
                            if any(
                                indicator in decoded.lower()
                                for indicator in [
                                    "writing at",
                                    "uploading",
                                    "%",
                                    "bytes",
                                    "compressed",
                                ]
                            ):
                                upload_started.set()
                                notify_frontend(
                                    "uploading",
                                    "Upload in progress... You can release the BOOT button now.",
                                )

                        # ✅ Send ALL upload progress to frontend terminal
                        try:
                            webview.windows[0].evaluate_js(
                                f"window.__appendTerminalLog({decoded!r})"
                            )
                        except Exception as e:
                            print(f"[TerminalLog] JS error: {e}")

                # Run upload with progress monitoring
                process = await asyncio.create_subprocess_exec(
                    *pio_cmd + ["run", "-t", "upload", f"--upload-port={actual_port}"],
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    cwd=build_dir,
                    env=env,
                )

                stdout_data, stderr_data = [], []

                # Start monitoring tasks
                await asyncio.gather(
                    monitor_upload_output(process.stdout, stdout_data, upload_started),
                    monitor_upload_output(process.stderr, stderr_data, upload_started),
                    return_exceptions=True,
                )

                u_code = await process.wait()
                u_stdout = "\n".join(stdout_data)
                u_stderr = "\n".join(stderr_data)

                # If upload never technically "started" but completed successfully,
                # still mark it as started for UI consistency
                if u_code == 0 and not upload_started.is_set():
                    notify_frontend("uploading", "Upload completed successfully!")

                if u_code == 0:
                    notify_frontend(
                        "upload_done", "✅ Upload complete! Rebooting board..."
                    )
                    parsed["upload_success"] = True
                    parsed["upload_port"] = actual_port
                else:
                    notify_frontend("upload_failed", "❌ Upload failed.")
                    parsed["upload_success"] = False
                    parsed["upload_port"] = actual_port
            else:
                notify_frontend("error", "No valid serial port found.")
                print("❌ No valid serial port detected.")
                return {
                    "success": False,
                    "error": "No valid serial port found",
                    "message": "ESP32 not detected. Please reconnect and try again.",
                }

        notify_frontend("done", "Build process completed.")
        result = {
            "success": parsed["success"],
            "message": parsed.get("message", "Compilation completed"),
            "specs": parsed.get("specs", {}),
            "warnings": parsed.get("warnings", []),
            "suggestions": parsed.get("suggestions", []),
        }

        if not parsed["success"]:
            result["error"] = parsed.get("error", "Compilation failed")
            if parsed.get("errors"):
                result["errors"] = parsed["errors"]

        print(f"📊 Final result: {result}")
        return result

    except FileNotFoundError as e:
        error_msg = f"PlatformIO not installed: {e}"
        notify_frontend("error", error_msg)
        print(f"❌ {error_msg}")
        return {
            "success": False,
            "error": error_msg,
            "message": "PlatformIO installation required",
            "suggestions": [
                "Run PlatformIO installation",
                "Check if PlatformIO is properly configured",
            ],
        }

    except Exception as e:
        error_msg = f"Unexpected error during compilation: {e}"
        notify_frontend("error", error_msg)
        print(f"❌ {error_msg}")
        return {
            "success": False,
            "error": error_msg,
            "message": "Compilation failed due to unexpected error",
            "suggestions": [
                "Check the console for detailed error information",
                "Verify your Python code syntax",
                "Ensure all required libraries are available",
            ],
        }


def prepare_build_folder():
    # 🔑 safer: starter_template lives one level up from core/
    project_root = Path(__file__).resolve().parent.parent
    starter = project_root / "core" / "transpiler" / "runtime" / "starter_template"

    if not starter.exists():
        raise FileNotFoundError(f"Starter template not found at {starter}")

    build_dir = tempfile.mkdtemp(prefix="build_")
    print(f"📁 Copying starter template from {starter} to {build_dir}")
    shutil.copytree(str(starter), build_dir, dirs_exist_ok=True)
    return build_dir


def write_transpiled_code(transpiled: dict, build_dir: str):
    src_dir = os.path.join(build_dir, "src")
    include_dir = os.path.join(build_dir, "include")

    os.makedirs(src_dir, exist_ok=True)
    os.makedirs(include_dir, exist_ok=True)

    for filename, code in transpiled.items():
        if filename == "main.py":
            filepath = os.path.join(src_dir, "main.ino")
        else:
            filepath = os.path.join(include_dir, filename.replace(".py", ".h"))
        with open(filepath, "w") as f:
            f.write(code)
        print(f"📄 Wrote {filepath}")


def get_build_flags(platform: str):
    core_build_flags = ["-std=gnu++17"]

    PLATFORM_BUILD_FLAGS = {
        "espressif32": ["-DARDUINO_USB_MODE=1", "-DSPIFFS_USE_LEGACY=1"],
        "espressif8266": ["-DSPIFFS_USE_LEGACY=1"],
    }

    platform_flags = PLATFORM_BUILD_FLAGS.get(platform, [])
    return core_build_flags + platform_flags


def write_platformio_ini(
    board: str,
    platform: str,
    build_dir: str,
    upload_speed=921600,
    monitor_speed=115200,
    dependencies=None,
):
    platform = _get_relevant_platform_version(platform)
    if dependencies is None:
        dependencies = []

    all_deps = ["ArduinoJson@6.21.4"] + dependencies
    deps_block = "\n".join(f"  {dep}" for dep in all_deps)

    build_flags = get_build_flags(platform)
    build_flags_block = "\n".join(f"  {flag}" for flag in build_flags)

    build_unflags = ["-std=gnu++11", "-std=gnu++14", "-std=c++11", "-std=c++14"]
    build_unflags_block = "\n".join(f"  {flag}" for flag in build_unflags)

    content = (
        "[env:{board}]\n"
        "platform = {platform}\n"
        "board = {board}\n"
        "framework = arduino\n"
        "upload_speed = {upload_speed}\n"
        "monitor_speed = {monitor_speed}\n"
        "build_unflags =\n{build_unflags_block}\n\n"
        "build_flags =\n{build_flags_block}\n\n"
        "lib_deps =\n{deps_block}\n"
    ).format(
        board=board,
        platform=platform,
        upload_speed=upload_speed,
        monitor_speed=monitor_speed,
        build_unflags_block=build_unflags_block,
        build_flags_block=build_flags_block,
        deps_block=deps_block,
    )

    ini_path = os.path.join(build_dir, "platformio.ini")
    with open(ini_path, "w") as f:
        f.write(content)
    print(f"📝 Wrote platformio.ini to {ini_path}")

    with open(ini_path) as f:
        print("📄 Final platformio.ini content:\n" + f.read())


# Convenience function to check and install PlatformIO if needed
def ensure_platformio_installed(user_app_dir: str):
    """Ensure PlatformIO is installed, install if needed."""
    return install_platformio_once(user_app_dir)
