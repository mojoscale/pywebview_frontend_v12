import webview
import asyncio
import threading
import sys
from pathlib import Path
import json


# core imports
from core.utils import APP_WINDOW_NAME
from core.updater import start_update_checker, run_updater, APP_VERSION
from core.serial_manager import is_serial_port_connected


class Api:
    def run_update(self, download_url):
        # Call your run_updater() function here
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
            index_path = Path(__file__).parent / "core" / "core_modules_index.json"
            if not index_path.exists():
                return {
                    "success": False,
                    "error": f"Index file not found at {index_path}",
                }

            with open(index_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            return data

        except Exception as e:
            # Optional: log the error
            print(f"[get_module_index ERROR] {e}")
            return e


if __name__ == "__main__":
    DEV = "--dev" in sys.argv
    api = Api()

    print(f"starting in dev  mode = {DEV}")

    if DEV:
        window_url = "http://localhost:5173"

    else:
        frontend_path = Path(__file__).parent / "frontend" / "dist" / "index.html"
        window_url = frontend_path.as_uri()
        # window_url = Path(__file__).parent / "frontend" / "dist"

    # ✅ This runs everything in the main thread
    window = webview.create_window(APP_WINDOW_NAME, url=window_url, js_api=api)
    # api.set_window(window)

    # ✅ Start an asyncio event loop BEFORE PyWebView UI starts
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    api.main_loop = loop  # save loop to api instance

    # ✅ Run asyncio loop in a thread
    threading.Thread(target=loop.run_forever, daemon=True).start()

    # Start update checker in background
    start_update_checker(window, interval=3600)  # check every 1h

    # ✅ Now safely start PyWebView on main thread
    webview.start(debug=DEV, http_server=True, private_mode=False)
