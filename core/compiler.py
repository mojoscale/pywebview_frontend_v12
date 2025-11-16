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
from core.transpiler.transpiler import main as transpiler_main
from typing import Optional, Dict, Any, List
from enum import Enum
import time


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
]

# hide the terminal wondow from openeing for subprocess.


if os.name == "nt":
    _orig_popen = subprocess.Popen

    def _quiet_popen(*args, **kwargs):
        kwargs.setdefault("creationflags", 0)
        kwargs["creationflags"] |= subprocess.CREATE_NO_WINDOW
        startupinfo = kwargs.get("startupinfo") or subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        kwargs["startupinfo"] = startupinfo
        return _orig_popen(*args, **kwargs)

    subprocess.Popen = _quiet_popen


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CORE_LIBS_PATH = os.path.join(BASE_DIR, "transpiler", "core_libs")
STARTER_TEMPLATE = (
    Path(__file__).resolve().parent.parent
    / "core"
    / "transpiler"
    / "runtime"
    / "starter_template"
)

# =============================================================================
# Compiler Session System
# =============================================================================


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
        """Send structured compiler event to frontend."""
        event = CompilerEvent(phase, text, level)
        print(f"[{phase.value}] {text}")
        try:
            webview.windows[0].evaluate_js(
                f"window.__onCompilerEvent({event.to_dict()})"
            )
        except Exception:
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
    session = _active_sessions.get(session_id)
    if session:
        asyncio.create_task(session.cancel())
        return True
    return False


# =============================================================================
# Main Compile Routine
# =============================================================================


async def compile_project(
    py_files: dict,
    board: str,
    platform: str,
    user_app_dir: str,
    upload: bool = False,
    port=None,
    dependencies=None,
):
    """Unified compile + upload flow with event streaming and dependency support."""
    # print(f"compiling for {board}-{platform}-{framework}")
    session = create_session()

    try:
        # ---------------------------------------------------------------------
        # 1. Transpile
        # ---------------------------------------------------------------------
        await session.send(SessionPhase.BEGIN_TRANSPILE, "Transpiling Python code...")
        commit_hash = str(uuid.uuid4()).replace("-", "_")
        DB_CONN = sqlite3.connect(DB_PATH)
        transpiler = transpiler_main(
            commit_hash, DB_CONN, py_files, CORE_LIBS_PATH, platform
        )
        await session.send(SessionPhase.END_TRANSPILE, "Transpilation complete")

        files = transpiler["code"]
        dependencies = (dependencies or []) + transpiler.get("dependencies", [])
        embed_files = transpiler.get("embed_files", [])

        framework = transpiler.get("framework", "arduino")

        # ---------------------------------------------------------------------
        # 💡 NEW: Pretty-print the transpiled C++ code to terminal
        # ---------------------------------------------------------------------
        import textwrap

        print("\n==================== 🧩 Transpiled Arduino Code ====================\n")
        for name, code in files.items():
            # Determine file type
            ext = "cpp" if name == "main.py" else "h"
            file_label = f"{name.replace('.py', f'.{ext}')}"
            print(f"📄 {file_label}:\n")

            # Re-indent for nice visual display
            formatted = textwrap.indent(code.strip(), "    ")
            print(formatted)
            print("\n" + "-" * 70 + "\n")

        print("===================== ✅ End of Transpiled Code =====================\n")

        # ---------------------------------------------------------------------
        # 2. Build Environment Setup
        # ---------------------------------------------------------------------
        print(f"compiling for {board}-{platform}-{framework}")
        await session.send(SessionPhase.BEGIN_COMPILE, "Setting up build folder...")
        build_dir = prepare_build_folder(framework)
        write_transpiled_code(files, build_dir, framework)
        write_platformio_ini(
            board, platform, build_dir, dependencies, framework, embed_files=embed_files
        )
        await session.send(SessionPhase.BEGIN_COMPILE, "Build folder ready")

        # Get PlatformIO
        pio_cmd, pio_env = get_platformio_command(user_app_dir)
        env = os.environ.copy()
        env.update(pio_env)

        # ---------------------------------------------------------------------
        # 3. Compilation
        # ---------------------------------------------------------------------
        await session.send(SessionPhase.BEGIN_COMPILE, "Starting compilation...")
        cmd = pio_cmd + ["run"]

        # MODIFIED: Add CREATE_NO_WINDOW flag for Windows
        if sys.platform == "win32":
            session.process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=build_dir,
                env=env,
                creationflags=subprocess.CREATE_NO_WINDOW,
            )
        else:
            session.process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=build_dir,
                env=env,
            )

        stdout, stderr = [], []

        async def stream(pipe, collector):
            while True:
                line = await pipe.readline()
                if not line:
                    break
                decoded = line.decode(errors="ignore").rstrip()
                collector.append(decoded)
                await session.send(SessionPhase.BEGIN_COMPILE, decoded)

        await asyncio.gather(
            stream(session.process.stdout, stdout),
            stream(session.process.stderr, stderr),
        )
        code = await session.process.wait()
        session.process = None

        parsed = parse_platformio_result("\n".join(stdout), "\n".join(stderr))
        if not parsed["success"] or code != 0:
            await session.send(SessionPhase.ERROR, "Compilation failed", "error")
            return parsed

        await session.send(SessionPhase.END_COMPILE, "Compilation successful")

        # ---------------------------------------------------------------------
        # 4. Upload (fixed event logic)
        # ---------------------------------------------------------------------
        upload_success = False
        if upload:
            await session.send(SessionPhase.START_UPLOAD, "Starting upload...")

            actual_port = port or find_esp_serial_port()
            if not actual_port:
                await session.send(
                    SessionPhase.ERROR, "❌ No ESP device detected", "error"
                )
                return {"success": False, "error": "No ESP device found"}

            cmd = pio_cmd + ["run", "-t", "upload", f"--upload-port={actual_port}"]

            # MODIFIED: Add CREATE_NO_WINDOW flag for Windows
            if sys.platform == "win32":
                session.process = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    cwd=build_dir,
                    env=env,
                    creationflags=subprocess.CREATE_NO_WINDOW,
                )
            else:
                session.process = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    cwd=build_dir,
                    env=env,
                )

            out_lines = []

            async def monitor_upload(pipe):
                """Stream upload logs, emit `[uploading]` events, detect failure."""
                while True:
                    line = await pipe.readline()
                    if not line:
                        break
                    decoded = line.decode(errors="ignore").rstrip()
                    out_lines.append(decoded)

                    # Categorize based on message content
                    lower = decoded.lower()
                    if "error" in lower or "failed" in lower or "fatal" in lower:
                        await session.send(SessionPhase.ERROR, decoded, "error")
                    elif (
                        "uploading" in lower
                        or "serial port" in lower
                        or "hard resetting" in lower
                    ):
                        await session.send(SessionPhase.START_UPLOAD, decoded)
                    else:
                        await session.send(SessionPhase.START_UPLOAD, decoded)

            await asyncio.gather(
                monitor_upload(session.process.stdout),
                monitor_upload(session.process.stderr),
            )

            code = await session.process.wait()
            session.process = None
            combined_out = "\n".join(out_lines)

            if code == 0 and "failed" not in combined_out.lower():
                upload_success = True
                await session.send(SessionPhase.END_UPLOAD, "✅ Upload complete")
            else:
                await session.send(SessionPhase.ERROR, "❌ Upload failed", "error")
                await session.send(
                    SessionPhase.END_UPLOAD, "❌ Upload failed (check logs)", "error"
                )

        # ---------------------------------------------------------------------
        # 5. Done
        # ---------------------------------------------------------------------
        await session.send(SessionPhase.ALL_DONE, "All done")
        return {
            "success": parsed["success"] and (upload_success or not upload),
            "upload_success": upload_success,
            "specs": parsed.get("specs", {}),
            "message": "Process completed",
            "session_id": session.id,
        }

    except Exception as e:
        await session.send(SessionPhase.ERROR, f"Unexpected error: {e}", "error")
        return {"success": False, "error": str(e)}
    finally:
        _active_sessions.pop(session.id, None)


# =============================================================================
# Helpers
# =============================================================================


def prepare_build_folder(framework) -> str:
    """
    Prepare the build folder by copying the starter template.
    Inject or remove main.c depending on the framework.
    """

    print(f"preparing folder for {framework}")

    template = STARTER_TEMPLATE

    if not template.exists():
        raise FileNotFoundError(f"Starter template not found at {template}")

    # Create a fresh temp build directory
    build_dir = Path(tempfile.mkdtemp(prefix="build_"))
    shutil.copytree(template, build_dir, dirs_exist_ok=True)

    print(f"📁 Build folder prepared at {build_dir}")

    # Paths
    src_dir = build_dir / "src"
    main_c_path = src_dir / "main.c"

    # Ensure src folder exists
    src_dir.mkdir(parents=True, exist_ok=True)

    if framework == "espidf":
        # Write main.c (overwrite if exists)
        main_c_contents = """#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_system.h"
#include "Arduino.h"   // Provided by Arduino-as-component

void app_main(void) {
    // Initialize Arduino runtime
    initArduino();

    // After this, Arduino infrastructure launches your setup() and loop() 
    // inside its own FreeRTOS tasks. Nothing else required here.
}
"""
        with open(main_c_path, "w", encoding="utf-8") as f:
            f.write(main_c_contents)

        print("📝 Created src/main.c for ESP-IDF + Arduino-as-component")

    elif framework == "arduino":
        # Remove main.c if present (to avoid duplicate main.o)
        if main_c_path.exists():
            main_c_path.unlink()
            print("🧹 Removed src/main.c (Arduino mode)")

    else:
        print(f"⚠ Unknown framework '{framework}', leaving src/ untouched")

    return str(build_dir)


def write_transpiled_code(files: dict, build_dir: str, framework):
    """Write .ino and .h files into src/include as per PlatformIO structure."""

    src_dir = os.path.join(build_dir, "src")

    if framework == "espidf":
        src_dir = os.path.join(build_dir, "lib", "ArduinoComponent")

    include_dir = os.path.join(build_dir, "include")
    os.makedirs(src_dir, exist_ok=True)
    os.makedirs(include_dir, exist_ok=True)

    for name, code in files.items():
        if name == "main.py":
            out_path = os.path.join(src_dir, "main.cpp")
        else:
            out_path = os.path.join(include_dir, name.replace(".py", ".h"))
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(code)
        print(f"✍️ Wrote {out_path}")


def write_platformio_ini(
    board: str,
    platform: str,
    build_dir: str,
    dependencies: list,
    framework: str,
    embed_files=[],
):
    deps = ["ArduinoJson@6.21.4"] + list(set(dependencies or []))
    build_flags = CORE_BUILD_FLAGS
    unflags = ["-std=gnu++11", "-std=gnu++14", "-Werror"]

    framework_to_add = framework

    if framework == "espidf":
        framework_to_add = "espidf, arduino"  # for using espidf, we use arduino as a component in espidf

    source_folder = "src"

    if framework == "espidf":
        source_folder = "main"
        build_flags += ESPIDF_BUILD_FLAGS

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
    )

    if embed_files:
        ini += "board_build.embed_files=\n  " + "\n  ".join(embed_files) + "\n"

    if framework == "espidf":
        ini += "board_build.sdkconfig = sdkconfig.defaults\n"
        # ini += "platform_packages = framework-espidf @ 5.1.2\n"

    ini_path = os.path.join(build_dir, "platformio.ini")
    with open(ini_path, "w", encoding="utf-8") as f:
        f.write(ini)
    print(f"📝 platformio.ini written to {ini_path}")
    print(ini)


def get_platformio_command(user_app_dir: str):
    pio_home = os.path.join(user_app_dir, ".platformio")
    venv = os.path.join(pio_home, "platformio_venv")
    exe = (
        os.path.join(venv, "Scripts", "python.exe")
        if sys.platform == "win32"
        else os.path.join(venv, "bin", "python")
    )
    env = os.environ.copy()
    env["PLATFORMIO_CORE_DIR"] = pio_home
    return [exe, "-c", "import platformio.__main__; platformio.__main__.main()"], env


def parse_platformio_result(stdout: str, stderr: str) -> dict:
    """Basic parser for PlatformIO build output."""
    combined = stdout + "\n" + stderr
    failed = any("error:" in line.lower() for line in combined.splitlines())
    result = {
        "success": not failed,
        "message": "Build success" if not failed else "Build failed",
        "specs": {},
    }
    # (Memory parse optional here)
    return result


def parse_upload_result(code: int, stdout: str, stderr: str) -> bool:
    """Check upload success."""
    return code == 0 or "Hard resetting" in stdout


def find_esp_serial_port() -> Optional[str]:
    ports = list(serial.tools.list_ports.comports())
    for p in ports:
        desc = p.description.lower() if p.description else ""
        if "esp32" in desc or "espressif" in desc or "cp210" in desc or "ch340" in desc:
            print(f"✅ ESP device detected at {p.device}")
            return p.device
    return ports[0].device if ports else None
