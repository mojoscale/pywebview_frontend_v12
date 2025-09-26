import webview
import asyncio
import threading
import sys
from pathlib import Path


# core imports
from core.utils import APP_WINDOW_NAME
from core.updater import start_update_checker, run_updater, APP_VERSION


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
