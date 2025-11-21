# ======================================================================
#   FULL MOJOSCALE COMPILE BACKEND
#   Ultra-short paths, full PIO bootstrap, all in <user_app_dir>/.cmp/
# ======================================================================

import shutil
import os
import subprocess
import asyncio
import sys
import uuid
import sqlite3
import serial.tools.list_ports
import webview
import time
import textwrap
from pathlib import Path
from enum import Enum
from typing import Optional, Dict, Any, List

from core.utils import get_bundled_python_exe
from core.db import db_path as DB_PATH
from core.transpiler.transpiler import main as transpiler_main
from core.utils import get_app_dir


# ============================================================================
# CONFIG — BUILD FLAGS
# ============================================================================
CORE_BUILD_FLAGS = [
    "-std=gnu++17",
    "-DCONFIG_ARDUINO_IS_ESP_IDF=1",
    "-DARDUINO_USB_MODE=1",
    "-DSPIFFS_USE_LEGACY=1",
]

ESPIDF_BUILD_FLAGS = [
    "-DCONFIG_SCCB_CLK_FREQ=100000",
    "-DCONFIG_SCCB_HARDWARE_I2C=1",
    "-DCONFIG_XCLK_FREQ=20000000",
    "-D CONFIG_SOC_RESERVED_MEMORY_REGION_SIZE=0x100000",
    "-D CONFIG_ESP32_DPORT_WORKAROUND=y",
    "-Wno-error",
    "-DCONFIG_OV7670_SUPPORT=1",
    "-DCONFIG_OV7725_SUPPORT=1",
    "-DCONFIG_SCCB_HARDWARE_I2C=1",
    "-DCONFIG_SCCB_HARDWARE_I2C_PORT=1",
    "-DCONFIG_ESP_HTTPS_SERVER_ENABLE=0",
]


# ============================================================================
# INTERNAL CMP DIR STRUCTURE
# ============================================================================
def init_cmp_dirs(user_app_dir: str):
    """
    Create and return:
    cmp_root   = <user_app_dir>/.cmp
    pio_home   = <user_app_dir>/.cmp/p
    build_root = <user_app_dir>/.cmp/t
    temp_root  = <user_app_dir>/.cmp/x
    """

    CMP_ROOT = Path(user_app_dir) / ".cmp"
    CMP_ROOT.mkdir(parents=True, exist_ok=True)

    PIO_HOME = CMP_ROOT / "p"
    BUILD_ROOT = CMP_ROOT / "t"
    TEMP_ROOT = CMP_ROOT / "x"

    PIO_HOME.mkdir(parents=True, exist_ok=True)
    BUILD_ROOT.mkdir(parents=True, exist_ok=True)
    TEMP_ROOT.mkdir(parents=True, exist_ok=True)

    return CMP_ROOT, PIO_HOME, BUILD_ROOT, TEMP_ROOT


# ============================================================================
# PLATFORMIO INSTALLER / BOOTSTRAP
# ============================================================================
def ensure_platformio_installed(PIO_HOME: Path):
    """
    Ensures PlatformIO Core is installed in:
        <user_app_dir>/.cmp/p/

    Using virtualenv:
        <user_app_dir>/.cmp/p/v/
    """
    VENV = PIO_HOME / "v"

    # Determine python.exe of the venv
    if sys.platform == "win32":
        python_exe = VENV / "Scripts" / "python.exe"
    else:
        python_exe = VENV / "bin" / "python"

    # If missing → create venv and install PlatformIO
    if not python_exe.exists():
        print("🚀 Creating PlatformIO virtual environment...")

        # Use system python to create the venv
        subprocess.run([sys.executable, "-m", "venv", str(VENV)], check=True)

        print("🚀 Upgrading pip...")
        subprocess.run(
            [str(python_exe), "-m", "pip", "install", "--upgrade", "pip"], check=True
        )

        print("🚀 Installing PlatformIO Core...")
        subprocess.run(
            [str(python_exe), "-m", "pip", "install", "platformio"], check=True
        )

        print("✔ PlatformIO installed successfully.")

    return python_exe


# ============================================================================
# WINDOWS: Hide subprocess windows
# ============================================================================
if os.name == "nt":
    _orig_popen = subprocess.Popen

    def _quiet_popen(*args, **kwargs):
        kwargs.setdefault("creationflags", 0)
        kwargs["creationflags"] |= subprocess.CREATE_NO_WINDOW
        si = kwargs.get("startupinfo") or subprocess.STARTUPINFO()
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        kwargs["startupinfo"] = si
        return _orig_popen(*args, **kwargs)

    subprocess.Popen = _quiet_popen


# ============================================================================
# SESSION SYSTEM
# ============================================================================
class SessionPhase(str, Enum):
    BEGIN_TRANSPILE = "begin_transpile"
    END_TRANSPILE = "end_transpile"
    BEGIN_COMPILE = "begin_compile"
    END_COMPILE = "end_compile"
    START_UPLOAD = "start_upload"
    END_UPLOAD = "end_upload"
    ALL_DONE = "all_done"
    ERROR = "error"
    CANCELLED = "cancelled"


class CompilerEvent:
    def __init__(self, phase: SessionPhase, text: str, level: str = "info"):
        self.phase = phase
        self.text = text
        self.level = level
        self.timestamp = time.time()

    def to_dict(self):
        return {
            "phase": self.phase.value,
            "text": self.text,
            "level": self.level,
            "timestamp": self.timestamp,
        }


class CompilerSession:
    def __init__(self, session_id: str = None):
        self.id = session_id or str(uuid.uuid4())
        self.process: Optional[asyncio.subprocess.Process] = None
        self.cancelled = False

    async def send(self, phase: SessionPhase, text: str, level: str = "info"):
        event = CompilerEvent(phase, text, level)
        print(f"[{phase.value}] {text}")

        try:
            webview.windows[0].evaluate_js(
                f"window.__onCompilerEvent({event.to_dict()})"
            )
        except:
            pass

    async def cancel(self):
        if self.cancelled:
            return
        self.cancelled = True

        if self.process and self.process.returncode is None:
            try:
                self.process.terminate()
                await asyncio.sleep(0.5)
                if self.process.returncode is None:
                    self.process.kill()
            except ProcessLookupError:
                pass

        await self.send(SessionPhase.CANCELLED, "Build cancelled by user", "warn")


_active_sessions: Dict[str, CompilerSession] = {}


def create_session() -> CompilerSession:
    s = CompilerSession()
    _active_sessions[s.id] = s
    return s


def cancel_session(session_id: str):
    sess = _active_sessions.get(session_id)
    if sess:
        asyncio.create_task(sess.cancel())
        return True
    return False


# ========================================================================
# BUILD FOLDER HANDLING — Updated for ESP-IDF + Arduino-as-component
# ========================================================================
"""def clone_arduino_component(component_dir: Path):
    
    arduino_dir = component_dir / "arduino"

    if arduino_dir.exists():
        print("🔁 Arduino component already exists, skipping clone.")
        return

    print("⬇️  Downloading Arduino-ESP32 v3.3.4 as ESP-IDF component...")

    subprocess.run(
        [
            "git",
            "clone",
            "--recursive",
            "https://github.com/espressif/arduino-esp32.git",
            str(arduino_dir),
        ],
        check=True,
    )

    # Optional: checkout specific version
    subprocess.run(["git", "checkout", "3.3.4"], cwd=str(arduino_dir), check=True)

    subprocess.run(
        ["git", "submodule", "update", "--init", "--recursive"],
        cwd=str(arduino_dir),
        check=True,
    )

    print(f"✔ Arduino ESP32 component installed at: {arduino_dir}")"""


def get_arduino_cache_dir(user_app_dir: Path) -> Path:
    """Get the persistent Arduino component cache directory"""
    return user_app_dir / ".arduino_component_cache"


def clone_arduino_component(component_dir: Path, user_app_dir: str):
    """
    Clone Arduino-ESP32 into components/arduino from cache if available
    """
    arduino_dir = component_dir / "arduino"

    if arduino_dir.exists():
        print("🔁 Arduino component already exists in build, skipping.")
        return

    # Get cache directory
    cache_dir = get_arduino_cache_dir(Path(user_app_dir))
    cache_dir.mkdir(parents=True, exist_ok=True)

    arduino_cache = cache_dir / "arduino-esp32"

    # Check if cache exists and is valid
    if arduino_cache.exists() and (arduino_cache / ".git").exists():
        print("📦 Using cached Arduino component...")
        try:
            # Verify it's the right version
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=str(arduino_cache),
                capture_output=True,
                text=True,
                check=True,
            )
            print(f"🔍 Cache commit: {result.stdout.strip()[:8]}")

            # Copy from cache to build directory
            shutil.copytree(arduino_cache, arduino_dir, symlinks=False)
            print("✅ Arduino component copied from cache")
            return

        except (subprocess.CalledProcessError, Exception) as e:
            print(f"⚠️  Cache corrupted, re-downloading: {e}")
            shutil.rmtree(arduino_cache, ignore_errors=True)

    # Download fresh if cache doesn't exist or is corrupted
    print("⬇️  Downloading Arduino-ESP32 v3.3.4 as ESP-IDF component...")

    try:
        subprocess.run(
            [
                "git",
                "clone",
                "--recursive",
                "https://github.com/espressif/arduino-esp32.git",
                str(arduino_cache),
            ],
            check=True,
        )

        # Checkout specific version
        subprocess.run(["git", "checkout", "3.3.4"], cwd=str(arduino_cache), check=True)

        subprocess.run(
            ["git", "submodule", "update", "--init", "--recursive"],
            cwd=str(arduino_cache),
            check=True,
        )

        # Now copy from cache to build
        shutil.copytree(arduino_cache, arduino_dir, symlinks=False)
        print(f"✅ Arduino ESP32 component installed and cached at: {arduino_cache}")

    except Exception as e:
        print(f"❌ Failed to clone Arduino component: {e}")
        # Clean up failed cache
        shutil.rmtree(arduino_cache, ignore_errors=True)
        raise


def prepare_build_folder(framework, BUILD_ROOT: Path, STARTER_TEMPLATE: Path) -> Path:
    """
    Prepare a build folder and inject Arduino-as-component when framework == espidf
    """

    user_app_dir = get_app_dir()

    build_id = str(uuid.uuid4())[:6]
    build_dir = BUILD_ROOT / build_id

    shutil.copytree(STARTER_TEMPLATE, build_dir, dirs_exist_ok=True)
    print(f"📁 Build folder prepared at {build_dir}")

    # ===========================================
    # ESP-IDF MODE → INSTALL ARDUINO COMPONENT
    # ===========================================
    if framework == "espidf":
        components_dir = build_dir / "components"
        components_dir.mkdir(parents=True, exist_ok=True)

        # Clone Arduino-as-component (with caching)
        try:
            clone_arduino_component(components_dir, user_app_dir)
        except Exception as e:
            print(f"❌ Failed to clone Arduino component: {e}")
            raise

        # ESP-IDF expects CMakeLists.txt in main/, so move transpilations there
        main_dir = build_dir / "main"
        main_dir.mkdir(exist_ok=True)

    else:
        src_dir = build_dir / "src"
        src_dir.mkdir(parents=True, exist_ok=True)

    return build_dir


def cleanup_build_folder(build_dir: Path):
    try:
        shutil.rmtree(build_dir, ignore_errors=True)
        print(f"🧹 Cleaned build folder {build_dir}")
    except:
        pass


# ============================================================================
# WRITE TRANSPILER OUTPUT
# ============================================================================
def write_transpiled_code(files: dict, build_dir: Path, framework: str):
    """if framework == "espidf":
        src_dir = build_dir / "lib" / "ArduinoComponent"
    else:
        src_dir = build_dir / "src"
    """

    if framework == "espidf":
        src_dir = build_dir / "main"

        include_dir = build_dir / "components" / "mojoscale_arduino" / "include"

    else:
        src_dir = build_dir / "src"

        include_dir = build_dir / "include"
    src_dir.mkdir(parents=True, exist_ok=True)
    include_dir.mkdir(parents=True, exist_ok=True)

    for name, code in files.items():
        if name == "main.py":
            out = src_dir / "main.cpp"
        else:
            out = include_dir / name.replace(".py", ".h")
        out.write_text(code, encoding="utf-8")
        print(f"✍️ Wrote {out}")


# ============================================================================
# WRITE platformio.ini
# ============================================================================


def find_managed_component_cert_paths(build_dir: Path) -> List[str]:
    """
    Auto-detect RainMaker/Insights certificates inside .pio subdirectories.
    Returns project-relative paths for embed_txtfiles.
    """
    crt_files = []
    root = build_dir

    # Search for *.crt under .pio
    for p in root.rglob("*.crt"):
        # Only include known folders
        if "managed_components" in p.parts:
            rel = p.relative_to(build_dir)
            crt_files.append(str(rel).replace("\\", "/"))

    return crt_files


def write_platformio_ini(
    board: str,
    platform: str,
    build_dir: Path,
    dependencies: list,
    framework: str,
    embed_files: list,
    TEMP_ROOT: Path,
):
    deps = ["ArduinoJson@6.21.4"] + list(set(dependencies or []))
    build_flags = CORE_BUILD_FLAGS
    unflags = ["-std=gnu++11", "-std=gnu++14", "-Werror"]
    embed_txtfiles = []

    framework_to_add = framework
    if framework == "espidf":
        framework_to_add = "espidf, arduino"
        platform = "https://github.com/pioarduino/platform-espressif32/releases/download/stable/platform-espressif32.zip"
        build_flags += ESPIDF_BUILD_FLAGS
        embed_txtfiles = [
            "managed_components/espressif__esp_insights/server_certs/https_server.crt",
            "managed_components/espressif__esp_rainmaker/server_certs/rmaker_mqtt_server.crt",
            "managed_components/espressif__esp_rainmaker/server_certs/rmaker_claim_service_server.crt",
            "managed_components/espressif__esp_rainmaker/server_certs/rmaker_ota_server.crt",
        ]

    ini = (
        f"[env:{board}]\n"
        f"platform = {platform}\n"
        f"board = {board}\n"
        f"framework = {framework_to_add}\n"
        f"upload_speed = 921600\n"
        f"monitor_speed = 115200\n"
        f"build_unflags =\n  " + "\n  ".join(unflags) + "\n\n"
        f"build_flags =\n  " + "\n  ".join(build_flags) + "\n\n"
        f"lib_deps =\n  " + "\n  ".join(deps) + "\n\n"
        f"board_build.embed_txtfiles =\n  " + "\n  ".join(embed_txtfiles) + "\n\n"
        f"build_cache_dir = {TEMP_ROOT}\n\n"
    )

    if embed_files:
        ini += "board_build.embed_files=\n  " + "\n  ".join(embed_files) + "\n"

    if framework == "espidf":
        ini += "board_build.sdkconfig = sdkconfig.defaults\n"
        ini += f"build_src_filter = +<main/>\n"
        # ini += "board_build.arduino = enabled\n"
        # ini += "idf_components = espressif/arduino-esp32@^3.3.4"

    print(ini)

    (build_dir / "platformio.ini").write_text(ini, encoding="utf-8")
    print("📝 platformio.ini written")


def write_sdkconfig_defaults(build_dir: Path):
    sdk = build_dir / "sdkconfig.defaults"
    text = """\
CONFIG_FREERTOS_HZ=1000
CONFIG_NEWLIB_STDOUT_LINE_ENDING_CRLF=y
CONFIG_NEWLIB_STDERR_LINE_ENDING_CRLF=y
CONFIG_BT_ENABLED=n
CONFIG_SCCB_CLK_FREQ=100000
CONFIG_SCCB_HARDWARE_I2C=y
CONFIG_SCCB_HARDWARE_I2C_PORT=1

"""
    sdk.write_text(text, encoding="utf-8")
    print(f"📝 sdkconfig.defaults written at {sdk}")


# ============================================================================
# GET PLATFORMIO COMMAND
# ============================================================================
def get_platformio_command(PIO_HOME: Path):
    python_exe = ensure_platformio_installed(PIO_HOME)

    env = {
        "PLATFORMIO_HOME": str(PIO_HOME),
        "PIO_HOME_DIR": str(PIO_HOME),
        "PLATFORMIO_CORE_DIR": str(PIO_HOME),
    }

    cmd = [
        str(python_exe),
        "-c",
        "import platformio.__main__; platformio.__main__.main()",
    ]

    return cmd, env


# ============================================================================
# UPLOAD PORT DETECTION
# ============================================================================
def find_esp_serial_port() -> Optional[str]:
    ports = list(serial.tools.list_ports.comports())
    for p in ports:
        desc = (p.description or "").lower()
        if any(x in desc for x in ["esp", "ch340", "cp210"]):
            return p.device
    return ports[0].device if ports else None


# ============================================================================
# PARSE RESULT
# ============================================================================
def parse_platformio_result(stdout: str, stderr: str):
    combined = stdout + "\n" + stderr
    failed = any("error:" in line.lower() for line in combined.splitlines())
    return {
        "success": not failed,
        "message": "Build success" if not failed else "Build failed",
        "specs": {},
    }


# ============================================================================
# MAIN COMPILE ROUTINE
# ============================================================================
async def compile_project(
    py_files: dict,
    board: str,
    platform: str,
    user_app_dir: str,
    upload: bool = False,
    port=None,
    dependencies=None,
):
    # INIT PATH STRUCTURE
    CMP_ROOT, PIO_HOME, BUILD_ROOT, TEMP_ROOT = init_cmp_dirs(user_app_dir)

    session = create_session()

    try:
        # -----------------------------------------------------------
        # 1. TRANSPILATION
        # -----------------------------------------------------------
        await session.send(SessionPhase.BEGIN_TRANSPILE, "Transpiling Python code...")

        commit_hash = str(uuid.uuid4()).replace("-", "_")
        DB_CONN = sqlite3.connect(DB_PATH)

        transpiler = transpiler_main(
            commit_hash,
            DB_CONN,
            py_files,
            os.path.join(os.path.dirname(__file__), "transpiler", "core_libs"),
            platform,
        )

        files = transpiler["code"]
        dependencies = (dependencies or []) + transpiler.get("dependencies", [])
        embed_files = transpiler.get("embed_files", [])
        framework = transpiler.get("framework", "arduino")

        await session.send(SessionPhase.END_TRANSPILE, "Transpilation complete")

        # -----------------------------------------------------------
        # 2. BUILD FOLDER SETUP
        # -----------------------------------------------------------
        if framework == "espidf":
            STARTER_TEMPLATE = (
                Path(__file__).resolve().parent.parent
                / "core"
                / "transpiler"
                / "runtime"
                / "starter_template_espidf"
            )
        else:
            STARTER_TEMPLATE = (
                Path(__file__).resolve().parent.parent
                / "core"
                / "transpiler"
                / "runtime"
                / "starter_template"
            )

        await session.send(SessionPhase.BEGIN_COMPILE, "Preparing build folder...")
        build_dir = prepare_build_folder(framework, BUILD_ROOT, STARTER_TEMPLATE)

        write_transpiled_code(files, build_dir, framework)
        if framework == "espidf":
            write_sdkconfig_defaults(build_dir)
        write_platformio_ini(
            board,
            platform,
            build_dir,
            dependencies,
            framework,
            embed_files,
            TEMP_ROOT,
        )

        # -----------------------------------------------------------
        # 3. RUN PLATFORMIO
        # -----------------------------------------------------------
        await session.send(SessionPhase.BEGIN_COMPILE, "Starting compilation...")

        pio_cmd, pio_env = get_platformio_command(PIO_HOME)

        env = os.environ.copy()
        env.update(pio_env)
        env["TMP"] = str(TEMP_ROOT)
        env["TEMP"] = str(TEMP_ROOT)

        cmd = pio_cmd + ["run"]

        session.process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=str(build_dir),
            env=env,
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
        )

        stdout_lines = []
        stderr_lines = []

        async def stream(pipe, collector):
            while True:
                line = await pipe.readline()
                if not line:
                    break
                txt = line.decode(errors="ignore").rstrip()
                collector.append(txt)
                await session.send(SessionPhase.BEGIN_COMPILE, txt)

        await asyncio.gather(
            stream(session.process.stdout, stdout_lines),
            stream(session.process.stderr, stderr_lines),
        )

        code = await session.process.wait()
        session.process = None

        parsed = parse_platformio_result(
            "\n".join(stdout_lines), "\n".join(stderr_lines)
        )

        if code != 0 or not parsed["success"]:
            await session.send(SessionPhase.ERROR, "Compilation failed", "error")
            cleanup_build_folder(build_dir)
            return parsed

        await session.send(SessionPhase.END_COMPILE, "Compilation successful")

        # -----------------------------------------------------------
        # 4. UPLOAD
        # -----------------------------------------------------------
        upload_success = False

        if upload:
            await session.send(SessionPhase.START_UPLOAD, "Starting upload...")

            actual_port = port or find_esp_serial_port()
            if not actual_port:
                await session.send(SessionPhase.ERROR, "No ESP32 device found", "error")
                cleanup_build_folder(build_dir)
                return {"success": False}

            cmd = pio_cmd + [
                "run",
                "-t",
                "upload",
                f"--upload-port={actual_port}",
            ]

            session.process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(build_dir),
                env=env,
                creationflags=subprocess.CREATE_NO_WINDOW
                if sys.platform == "win32"
                else 0,
            )

            out_lines = []

            async def stream_u(pipe):
                while True:
                    line = await pipe.readline()
                    if not line:
                        break
                    txt = line.decode(errors="ignore").rstrip()
                    out_lines.append(txt)
                    await session.send(SessionPhase.START_UPLOAD, txt)

            await asyncio.gather(
                stream_u(session.process.stdout),
                stream_u(session.process.stderr),
            )

            code = await session.process.wait()

            if code == 0:
                upload_success = True
                await session.send(SessionPhase.END_UPLOAD, "Upload complete")
            else:
                await session.send(SessionPhase.ERROR, "Upload failed", "error")

        # -----------------------------------------------------------
        # 5. CLEANUP + DONE
        # -----------------------------------------------------------
        cleanup_build_folder(build_dir)

        await session.send(SessionPhase.ALL_DONE, "All done")

        return {
            "success": True,
            "upload_success": upload_success,
            "message": "Process completed successfully",
            "session_id": session.id,
        }

    except Exception as e:
        await session.send(SessionPhase.ERROR, f"Unexpected error: {e}", "error")
        return {"success": False, "error": str(e)}

    finally:
        _active_sessions.pop(session.id, None)
