import webview
import asyncio
import threading
import sys
from pathlib import Path
from importlib import resources
import json
import os
import re

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
)

from core.transpiler.generate_pyi import generate_pyi_stubs, CORE_LIBS
from core.transpiler.lint_code import main as linter_main
from core.compiler import compile_project


CORE_LIBS_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "core", "transpiler", "core_libs"
)
CORE_STUBS_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "core", "transpiler", "core_stubs"
)


class Api:
    def __init__(self):
        self.is_packaged = getattr(sys, "frozen", False)
        self.main_loop = None
        self.compile_queue = None
        self.loop_ready = False

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
        create_new_project(
            project_details["name"], project_details["description"], metadata=metadata
        )

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
        self, code: str, line: int, column: int, stub_path: str = CORE_STUBS_PATH
    ):
        try:
            stub_path = str(Path(stub_path).resolve())

            # Extend sys.path with your stub folder
            extended_sys_path = [stub_path, *sys.path]

            project = jedi.Project(path=Path.cwd(), sys_path=extended_sys_path)

            script = jedi.Script(code, path="script.py", project=project)
            completions = script.complete(line + 1, column)

            return [
                {
                    "label": c.name,
                    "kind": c.type,
                    "detail": c.description,
                    "documentation": c.docstring(),
                    "insertText": c.name,
                }
                for c in completions
            ]
        except Exception as e:
            return {"error": str(e)}

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
    def compile(self, project_id, upload=False, port=None):
        """Schedule a compile job and return immediately."""
        project = get_project_from_id(project_id)
        if not project:
            return {"success": False, "error": f"Project {project_id} not found."}

        board = project["metadata"].get("board_id")
        platform = project["metadata"].get("platform")
        code_files = {"main.py": get_project_code_from_id(project_id)}

        if not board or not platform:
            return {
                "success": False,
                "error": "Board/platform not set in project metadata",
            }

        task = {
            "project_id": project_id,
            "board": board,
            "platform": platform,
            "code_files": code_files,
            "upload": upload,
            "port": port,
        }

        if not self.loop_ready:
            return {"success": False, "error": "Main loop not ready"}

        # Push into async compile queue
        self.main_loop.call_soon_threadsafe(self.compile_queue.put_nowait, task)
        return {"success": True, "message": "Compilation scheduled"}

    async def compile_worker(self):
        """Background worker to process compile tasks sequentially."""
        self.loop_ready = True
        while True:
            task = await self.compile_queue.get()
            try:
                print(
                    f"⚡ Compiling project {task['project_id']} "
                    f"for board={task['board']}, platform={task['platform']}"
                )
                result = await compile_project(
                    task["code_files"],
                    task["board"],
                    task["platform"],
                    user_app_dir=str(get_app_dir()),
                    upload=task["upload"],
                    port=task["port"],
                )

                # Ensure JSON-safe
                safe_result = {}
                for k, v in result.items():
                    if isinstance(v, (str, int, float, bool, type(None), list, dict)):
                        safe_result[k] = v
                    else:
                        safe_result[k] = str(v)

                print(f"✅ Compile finished: {safe_result}")
                # TODO: push to frontend via evaluate_js if desired
            except Exception as e:
                print(f"❌ Compile failed: {e}")
            finally:
                self.compile_queue.task_done()


# ------------------------
# Main entry
# ------------------------
if __name__ == "__main__":
    check_or_create_app_dir()

    DEV = "--dev" in sys.argv
    api = Api()

    print(f"Starting in dev mode = {DEV}")

    if DEV:
        window_url = "http://localhost:5173"
        generate_pyi_stubs(CORE_LIBS)
    else:
        frontend_path = Path(__file__).parent / "frontend" / "dist" / "index.html"
        window_url = frontend_path.as_uri()

    window = webview.create_window(APP_WINDOW_NAME, url=window_url, js_api=api)

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
