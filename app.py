import webview
import asyncio
import threading
import sys
from pathlib import Path
from importlib import resources
import json
import os
import re
import serial
import serial.tools.list_ports
import time

import jedi

# core imports
from core.utils import (
    APP_WINDOW_NAME,
    check_or_create_app_dir,
    get_available_platforms,
    get_available_boards,
    get_platform_for_board_id,
    get_app_dir,
)
from core.updater import start_update_checker, run_updater, APP_VERSION
from core.serial_manager import is_serial_port_connected
from core.db import (
    create_new_project,
    get_all_projects,
    get_project_from_id,
    get_core_db_conn,
    update_project_files,
    get_project_code_from_id,
    update_project_details,
)

from core.transpiler.generate_pyi import generate_pyi_stubs, CORE_LIBS
from core.transpiler.lint_code import main as linter_main
from core.compiler import compile_project
from core.env_manager import (
    get_all,
    get_value,
    create_value,
    update_value,
    delete_value,
    bulk_create,
    bulk_update,
)

from core.core_modules_index_generator import main as docs_generator
from core.completions import get_python_completions
from core.serial_manager import get_valid_serial_port

# Detect packaged app
if getattr(sys, "frozen", False):
    # Running as packaged executable (Nuitka/PyInstaller)
    BASE_DIR = Path(sys.executable).parent
else:
    # Running as normal Python
    BASE_DIR = Path(__file__).parent


CORE_LIBS_PATH = os.path.join(BASE_DIR, "core", "transpiler", "core_libs")
CORE_STUBS_PATH = os.path.join(BASE_DIR, "core", "transpiler", "core_stubs")


# Serial monitor
_serial_instance = None
_monitor_thread = None
_monitoring = False
_connected_port = None
_log_callback = None  # set by frontend via pywebview.expose()


class Api:
    def __init__(self):
        self.is_packaged = getattr(sys, "frozen", False)
        self.main_loop = None
        self.compile_queue = None
        self.loop_ready = False
        self.compile_status = {}

    # ------------------------
    # General app utils
    # ------------------------
    def run_update(self, download_url):
        print("⚡ Triggering update from frontend")
        run_updater(download_url)
        return {"status": "started"}

    def get_version(self):
        return APP_VERSION

    # ------------------------
    # Projects
    # ------------------------
    def get_projects(self):
        return get_all_projects()

    def get_project(self, project_id):
        return get_project_from_id(project_id)

    def create_project(self, project_details):
        metadata = {}
        if "board_name_id" in project_details:
            board_name_id = project_details["board_name_id"]
            match = re.match(r"^(.*)\s+\((.*)\)$", board_name_id)
            board_name = match.group(1).strip()
            board_id = match.group(2).strip()
            platform = get_platform_for_board_id(board_id)
            metadata["board_name"] = board_name
            metadata["board_id"] = board_id
            metadata["platform"] = platform

            description = ""

            if "description" in project_details:
                description = project_details["description"]
        create_new_project(project_details["name"], description, metadata=metadata)

    def update_project(self, payload: dict):
        return update_project_details(payload)

    # ------------------------
    # Serial + Modules
    # ------------------------
    def serial_port_available(self):
        return is_serial_port_connected()

    def get_module_index(self):
        try:
            with resources.files("core").joinpath("core_modules_index.json").open(
                "r", encoding="utf-8"
            ) as f:
                data = json.load(f)
            print(f"Loaded module index: {len(data.get('modules', []))} modules")
            return data
        except Exception as e:
            print(f"[get_module_index ERROR] {e}")
            return {"success": False, "error": str(e)}

    # ------------------------
    # Platforms + Boards
    # ------------------------
    def get_platforms(self):
        return get_available_platforms()

    def get_boards(self):
        return get_available_boards()

    # ------------------------
    # Linting
    # ------------------------
    def lint_code(self, code: str, platform):
        print(f"🔎 Linting code for {platform}")
        conn = get_core_db_conn()
        errors = linter_main(code, conn, platform, CORE_LIBS_PATH)
        print(f"Errors: {errors}")
        return errors

    def get_completions(
        self,
        code: str = None,
        line: int = None,
        column: int = None,
        stub_path: str = CORE_STUBS_PATH,
    ):
        return []
        """try:
            # Parameter validation and correction
            if isinstance(line, str) and "\n" in line:
                # line parameter actually contains code - parameters are shifted
                actual_code = line
                actual_line = column
                actual_column = stub_path
                actual_stub_path = CORE_STUBS_PATH

                # Update the variables
                code = actual_code
                line = actual_line
                column = actual_column
                stub_path = actual_stub_path

            # Safe conversion with extensive error handling
            try:
                if line is None:
                    line_num = 0
                elif isinstance(line, int):
                    line_num = line
                elif isinstance(line, str) and line.strip().isdigit():
                    line_num = int(line.strip())
                else:
                    line_num = 0
            except (TypeError, ValueError) as e:
                line_num = 0

            try:
                if column is None:
                    col_num = 0
                elif isinstance(column, int):
                    col_num = column
                elif isinstance(column, str) and column.strip().isdigit():
                    col_num = int(column.strip())
                else:
                    col_num = 0
            except (TypeError, ValueError) as e:
                col_num = 0

            # Validate code
            if not code or not isinstance(code, str):
                return []

            # Pass the converted integers to get_python_completions
            result = get_python_completions(
                code, line_num, col_num, stub_path=stub_path
            )

            return result

        except Exception as e:
            import traceback

            print(f"❌ get_completions ERROR: {type(e).__name__}: {str(e)}")
            print("📋 Full traceback:")
            tb_lines = traceback.format_exc().split("\n")
            for line in tb_lines:
                if line.strip():
                    print(f"   {line}")
            return []"""

    def format_code_simple(self, code: str) -> str:
        """Lightweight fallback formatter (no external deps)."""
        try:
            lines = code.splitlines()
            result = []
            indent = 0
            in_str = False
            str_delim = None
            prev_blank = False

            for raw in lines:
                stripped = raw.strip()

                # skip consecutive blank lines
                if not stripped:
                    if not prev_blank:
                        result.append("")
                    prev_blank = True
                    continue
                prev_blank = False

                # detect triple-quoted strings
                for delim in ('"""', "'''"):
                    count = stripped.count(delim)
                    if count == 1:
                        in_str = not in_str
                        str_delim = delim
                    elif count >= 2 and in_str and delim == str_delim:
                        in_str = False

                if in_str:
                    result.append(raw)
                    continue

                first_word = stripped.split()[0] if stripped else ""

                if first_word in {"else", "elif", "except", "finally"}:
                    indent = max(0, indent - 1)
                elif first_word in {"return", "break", "continue", "pass", "raise"}:
                    orig_indent = (len(raw) - len(stripped)) // 4
                    if orig_indent < indent:
                        indent = orig_indent

                result.append("    " * indent + stripped)

                if stripped.endswith(":") and not stripped.startswith("@"):
                    indent += 1

            # remove leading/trailing blank lines
            return "\n".join([ln for ln in result]).strip("\n")
        except Exception as e:
            print(f"Format error: {e}")
            return code

    def format_code(self, code: str) -> str:
        """Format Python code using Black if available, else fallback."""
        try:
            import black

            mode = black.Mode()
            return black.format_str(code, mode=mode)
        except Exception as e:
            print(f"[Black unavailable or failed: {e}] using fallback formatter")
            return self.format_code_simple(code)

    # ------------------------
    # Project files
    # ------------------------
    def save_project_files(self, project_id, code):
        update_project_files(project_id, code)
        return

    def get_project_code(self, project_id):
        return get_project_code_from_id(project_id)

    # ------------------------
    # Compilation
    # ------------------------
    # Add to your __init__ method

    def compile(self, project_id, upload=False, port=None):
        """Schedule a compile job."""
        project = get_project_from_id(project_id)
        if not project:
            return {"success": False, "error": f"Project {project_id} not found"}

        board = project["metadata"].get("board_id")
        platform = project["metadata"].get("platform")
        code_files = {"main.py": get_project_code_from_id(project_id)}

        if not board or not platform:
            return {"success": False, "error": "Board/platform not set"}

        task = {
            "project_id": project_id,
            "board": board,
            "platform": platform,
            "code_files": code_files,
            "upload": upload,
            "port": port,
        }

        self.compile_status[project_id] = {
            "completed": False,
            "success": False,
            "in_progress": True,
            "message": "Compilation queued",
            "session_id": None,
        }

        if not self.loop_ready:
            return {"success": False, "error": "Main loop not ready"}

        self.main_loop.call_soon_threadsafe(self.compile_queue.put_nowait, task)
        return {"success": True, "message": "Compilation scheduled"}

    async def compile_worker(self):
        """Processes compile tasks sequentially."""
        self.loop_ready = True
        while True:
            task = await self.compile_queue.get()
            project_id = task["project_id"]

            try:
                result = await compile_project(
                    task["code_files"],
                    task["board"],
                    task["platform"],
                    user_app_dir=str(get_app_dir()),
                    upload=task["upload"],
                    port=task["port"],
                )

                session_id = result.get("session_id")
                self.compile_status[project_id] = {
                    "completed": True,
                    "success": result.get("success", False),
                    "in_progress": False,
                    "message": result.get("message", "Done"),
                    "session_id": session_id,
                    "error": result.get("error"),
                    "warnings": result.get("warnings", []),
                    "specs": result.get("specs", {}),
                    "suggestions": result.get("suggestions", []),
                }

            except Exception as e:
                self.compile_status[project_id] = {
                    "completed": True,
                    "success": False,
                    "in_progress": False,
                    "error": str(e),
                }
            finally:
                self.compile_queue.task_done()

    def get_compile_status(self, project_id):
        """Get current compile or upload state."""
        return self.compile_status.get(project_id, {"exists": False})

    def cancel_compile(self, project_id):
        """Cancel an ongoing compilation."""
        status = self.compile_status.get(project_id)
        if not status or not status.get("session_id"):
            return {"success": False, "error": "No active session"}
        session_id = status["session_id"]
        ok = cancel_session(session_id)
        if ok:
            status["in_progress"] = False
            status["completed"] = True
            status["success"] = False
            status["message"] = "Cancelled by user"
            return {"success": True, "message": "Cancelled"}
        return {"success": False, "error": "Session not found or inactive"}

    # ------------------------
    # Environment Variables
    # ------------------------
    def get_all_env(self):
        """Return all environment variables."""
        return get_all()

    def get_env_value(self, key):
        """Return a single environment variable."""
        return get_value(key)

    def create_env_value(self, key, value, is_secret=False):
        """Create a new environment variable."""
        return create_value(key, value, is_secret)

    def update_env_value(self, key, value=None, is_secret=None):
        """Update an existing environment variable."""
        return update_value(key, value, is_secret)

    def delete_env_value(self, key):
        """Delete a specific environment variable."""
        return delete_value(key)

    def bulk_create_env(self, pairs):
        """Create multiple environment variables at once."""
        return bulk_create(pairs)

    def bulk_update_env(self, pairs):
        """Update multiple environment variables at once."""
        return bulk_update(pairs)

    # ==========================================================
    # SERIAL MONITOR SECTION
    # ==========================================================
    def start_serial_monitor(self, baudrate=115200):
        """Auto-detect serial port and start background monitor."""
        global _serial_instance, _monitor_thread, _monitoring, _connected_port

        if _monitoring:
            return {"status": "already_running"}

        port = get_valid_serial_port()
        if not port:
            return {"status": "error", "message": "No valid serial port found"}

        try:
            _serial_instance = serial.Serial(port, baudrate, timeout=0.1)
            _connected_port = port
            _monitoring = True

            _monitor_thread = threading.Thread(
                target=self._serial_monitor_loop, daemon=True
            )
            _monitor_thread.start()

            print(f"✅ Serial connected automatically to {port}")
            return {"status": "connected", "port": port}

        except Exception as e:
            return {"status": "error", "message": str(e)}

    def _serial_monitor_loop(self):
        """Continuously read serial and push lines to the frontend."""
        import json, webview

        global _serial_instance, _monitoring, _connected_port

        while _monitoring and _serial_instance:
            try:
                if _serial_instance.in_waiting:
                    line = _serial_instance.readline().decode(errors="ignore").strip()
                    if line:
                        print(f"[SERIAL] {line}")  # backend log for debugging

                        # 🚀 Send to frontend as a CustomEvent
                        script = (
                            f"window.dispatchEvent(new CustomEvent('serial-log', "
                            f"{{ detail: {json.dumps(line)} }}));"
                        )
                        try:
                            webview.windows[0].evaluate_js(script)
                        except Exception as e:
                            print(f"[EVAL ERROR] {e}")
                else:
                    time.sleep(0.05)

            except Exception as e:
                print(f"[SERIAL ERROR] {e}")
                break

        print(f"🔴 Serial disconnected from {_connected_port}")
        _monitoring = False
        _connected_port = None

    def stop_serial_monitor(self):
        """Stop serial monitor and close port."""
        global _serial_instance, _monitoring, _connected_port
        _monitoring = False
        if _serial_instance:
            try:
                _serial_instance.close()
            except Exception:
                pass
        _connected_port = None
        print("🛑 Serial monitor stopped")
        return {"status": "stopped"}

    def send_serial_command(self, command: str):
        """Send a command string to the current serial device."""
        global _serial_instance
        if not _serial_instance:
            return {"status": "error", "message": "No active serial connection"}

        try:
            _serial_instance.write((command + "\n").encode())
            return {"status": "ok", "sent": len(command)}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def register_serial_callback(self):
        """
        Frontend calls this once to register a Python-side event forwarder.
        The callback will emit serial lines to JS via evaluate_js.
        """
        import webview

        global _log_callback

        def _callback(line):
            # Emit to JS as a custom event
            script = f"window.dispatchEvent(new CustomEvent('serial-log', {{ detail: {json.dumps(line)} }}))"
            webview.windows[0].evaluate_js(script)

        _log_callback = _callback
        print("📡 Serial callback registered")
        return {"status": "registered"}


# ------------------------
# Main entry
# ------------------------
if __name__ == "__main__":
    check_or_create_app_dir()
    generate_pyi_stubs(CORE_LIBS)
    docs_generator()

    DEV = "--dev" in sys.argv
    api = Api()

    print(f"Starting in dev mode = {DEV}")

    if DEV:
        window_url = "http://localhost:5173"

    else:
        frontend_path = Path(__file__).parent / "frontend" / "dist" / "index.html"
        window_url = frontend_path.as_uri()

    window = webview.create_window(
        APP_WINDOW_NAME,
        url=window_url,
        js_api=api,
    )

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    api.main_loop = loop
    api.compile_queue = asyncio.Queue()

    # Start compile worker
    loop.create_task(api.compile_worker())
    threading.Thread(target=loop.run_forever, daemon=True).start()

    # Start update checker
    start_update_checker(window, interval=3600)

    # Launch webview
    webview.start(debug=DEV, http_server=True, private_mode=False)
