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
from .utils import get_bundled_python_exe
from .db import db_path as DB_PATH


from core.transpiler.transpiler import main as transpiler_main

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CORE_LIBS_PATH = os.path.join(BASE_DIR, "transpiler", "core_libs")


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
    return ports[0].device  # e.g., 'COM3' or '/dev/ttyUSB0'


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
    result = {
        "success": "[SUCCESS]" in stdout,
        "firmware_bin": None,
        "firmware_elf": None,
        "ram_used": None,
        "flash_used": None,
        "duration_seconds": None,
        "errors": [],
        "warnings": [],
    }

    lines_out = stdout.splitlines()
    lines_err = stderr.splitlines()

    for line in lines_out:
        if "firmware.elf" in line and "Linking" in line:
            result["firmware_elf"] = line.strip().split()[-1]
        elif "firmware.bin" in line and "Building" in line:
            result["firmware_bin"] = line.strip().split()[-1]
        elif "RAM:" in line:
            match = re.search(r"RAM:\s+\[[= ]+\]\s+([\d.]+%)", line)
            if match:
                result["ram_used"] = match.group(1)
        elif "Flash:" in line:
            match = re.search(r"Flash:\s+\[[= ]+\]\s+([\d.]+%)", line)
            if match:
                result["flash_used"] = match.group(1)
        elif "[SUCCESS]" in line and "Took" in line:
            match = re.search(r"Took ([\d.]+) seconds", line)
            if match:
                result["duration_seconds"] = float(match.group(1))

    for line in lines_err:
        if "error:" in line.lower():
            result["errors"].append(line.strip())
        elif "warning:" in line.lower():
            result["warnings"].append(line.strip())

    return result


async def compile_project(
    py_files: dict,
    board: str,
    platform: str,
    user_app_dir: str,
    upload: bool = False,
    port=None,
    dependencies=None,
):
    commit_hash = str(uuid.uuid4()).replace("-", "_")
    DB_CONN = sqlite3.connect(DB_PATH)

    transpiler = transpiler_main(
        commit_hash, DB_CONN, py_files, CORE_LIBS_PATH, platform
    )

    files = transpiler["code"]
    dependencies = transpiler["dependencies"]
    print("📦 Starting compilation...")

    pio_home = os.path.join(user_app_dir, ".platformio")
    python_exe = get_bundled_python_exe()
    print(f"🔍 Python exe: {python_exe}")

    # Get both the command AND the environment
    pio_cmd, pio_env = bootstrap_pio(python_exe, pio_home)

    build_dir = prepare_build_folder()
    print(f"📁 Build folder prepared: {build_dir}")
    write_transpiled_code(files, build_dir)
    print("✍️ Transpiled files written.")
    write_platformio_ini(board, platform, build_dir, dependencies=dependencies)
    print(f"📝 platformio.ini written for board '{board}'.")

    # Merge environments - THIS IS CRITICAL
    env = os.environ.copy()
    env.update(pio_env)  # Add the PYTHONPATH from bootstrap_pio
    env["PLATFORMIO_CORE_DIR"] = pio_home

    print(f"🚀 Running PlatformIO compile in: {build_dir}")
    print(f"🔍 Command: {' '.join(pio_cmd)}")
    print(f"🔍 PYTHONPATH: {env.get('PYTHONPATH', 'Not set')}")

    stdout, stderr, code = await stream_command_to_terminal(
        pio_cmd + ["run"], cwd=build_dir, env=env  # Make sure env is passed here
    )

    parsed = parse_platformio_result(stdout, stderr)
    parsed["success"] = code == 0

    if upload and code == 0:
        actual_port = port or find_first_serial_port()
        print(f"🧭 Selected serial port: {actual_port}")
        release_serial_port(actual_port)
        await asyncio.sleep(1)
        u_stdout, u_stderr, u_code = await stream_command_to_terminal(
            pio_cmd + ["run", "-t", "upload", f"--upload-port={actual_port}"],
            cwd=build_dir,
            env=env,  # Make sure env is passed here too
        )
        parsed["upload_success"] = u_code == 0
        parsed["upload_port"] = actual_port

    return {
        **parsed,
        "board": board,
        "platform": platform,
        "build_dir": str(build_dir),
        "returncode": code,
    }


def bootstrap_pio(python_exe: str, pio_home: str):
    target_dir = os.path.join(pio_home, "platformio_packages")
    os.makedirs(target_dir, exist_ok=True)

    # Check if already installed
    if is_platformio_installed(target_dir):
        print("🟢 PlatformIO already installed.")
        env = {"PYTHONPATH": target_dir + os.pathsep + os.environ.get("PYTHONPATH", "")}
        return [python_exe, "-m", "platformio"], env

    print(f"📦 Installing PlatformIO to: {target_dir}")
    install_cmd = [
        python_exe,
        "-m",
        "pip",
        "install",
        "--target",
        target_dir,
        "platformio",
    ]
    subprocess.run(install_cmd, check=True)

    env = {"PYTHONPATH": target_dir + os.pathsep + os.environ.get("PYTHONPATH", "")}
    return [python_exe, "-m", "platformio"], env


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
