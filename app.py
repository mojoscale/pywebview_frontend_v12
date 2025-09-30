import webview
import asyncio
import threading
import sys
from pathlib import Path
from importlib import resources
import json
import os


# core imports
from core.utils import APP_WINDOW_NAME, check_or_create_app_dir, get_available_platforms
from core.updater import start_update_checker, run_updater, APP_VERSION
from core.serial_manager import is_serial_port_connected
from core.db import (
    create_new_project,
    get_all_projects,
    get_project_from_id,
    get_core_db_conn,
)

from core.transpiler.generate_pyi import generate_pyi_stubs, CORE_LIBS

from core.transpiler.lint_code import main as linter_main


CORE_LIBS_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "core", "transpiler", "core_libs"
)
CORE_STUBS_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "core", "transpiler", "core_stubs"
)


class Api:
    def __init__(self):
        self.is_packaged = getattr(sys, "frozen", False)

    def run_update(self, download_url):
        print("⚡ Triggering update from frontend")
        run_updater(download_url)
        return {"status": "started"}

    def get_version(self):
        return APP_VERSION

    def get_projects(self):
        return get_all_projects()

    def get_project(self, projectId):
        return get_project_from_id(projectId)

    def create_project(self, project_details):
        metadata = {}
        if "platform" in project_details:
            metadata["platform"] = project_details["platform"]
        create_new_project(
            project_details["name"], project_details["description"], metadata=metadata
        )

    def serial_port_available(self):
        return is_serial_port_connected()

    def get_module_index(self):
        try:
            # "core" is the package where your JSON lives
            with resources.files("core").joinpath("core_modules_index.json").open(
                "r", encoding="utf-8"
            ) as f:
                data = json.load(f)

            print(f"Loaded module index: {len(data.get('modules', []))} modules")
            return data

        except Exception as e:
            print(f"[get_module_index ERROR] {e}")
            return {"success": False, "error": str(e)}

    def get_platforms(self):
        return get_available_platforms()

    def lint_code(self, code: str, platform):
        print(f"liniting code")

        conn = get_core_db_conn()
        platform = platform
        errors = linter_main(code, conn, platform, CORE_LIBS_PATH)

        print(f"errors are {errors}")

        return errors


if __name__ == "__main__":
    # pre - startups scripts
    check_or_create_app_dir()

    ########################
    DEV = "--dev" in sys.argv
    api = Api()

    print(f"starting in dev mode = {DEV}")

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

    threading.Thread(target=loop.run_forever, daemon=True).start()
    start_update_checker(window, interval=3600)
    webview.start(debug=DEV, http_server=True, private_mode=False)
