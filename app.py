import webview
import asyncio
import threading
import sys
from pathlib import Path
from importlib import resources
import json


# core imports
from core.utils import APP_WINDOW_NAME
from core.updater import start_update_checker, run_updater, APP_VERSION
from core.serial_manager import is_serial_port_connected


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
        return [
            {
                "id": "1",
                "name": "Arduino Sensor Logger",
                "description": "Logs temperature + humidity data every 5 seconds.",
                "lastUpdated": "2025-09-24",
                "status": "Active",
            },
            {
                "id": "2",
                "name": "3D Printer Controller",
                "description": "Controls printer speed, motors, and temp sensors.",
                "lastUpdated": "2025-09-20",
                "status": "Inactive",
            },
        ]

    def create_project(self, project_details):
        print(f"receieved -- {project_details}")

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


if __name__ == "__main__":
    DEV = "--dev" in sys.argv
    api = Api()

    print(f"starting in dev mode = {DEV}")

    if DEV:
        window_url = "http://localhost:5173"
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
