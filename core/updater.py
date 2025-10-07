import requests
import threading
import time
import json
import os
import sys
import tempfile
import subprocess

# Keep this in sync with your build script
APP_VERSION = "0.1.0"
# Your server endpoint that returns {"version": "...", "download_url": "..."}
BASE_SERVER_URL = "https://mojoscale-1c7e8.web.app"
UPDATE_URL = f"{BASE_SERVER_URL}/latest_version.json"


def _is_newer(latest, current):
    """Compare two version strings like 1.0.0 vs 1.2.0."""
    try:
        latest_parts = [int(x) for x in latest.split(".")]
        current_parts = [int(x) for x in current.split(".")]
        return latest_parts > current_parts
    except Exception:
        # fallback: string comparison
        return latest != current


def check_for_updates(window=None):
    """Check once and notify frontend if an update is available."""
    try:
        r = requests.get(UPDATE_URL, timeout=5)
        data = r.json()

        latest_version = data["version"]

        if _is_newer(latest_version, APP_VERSION):
            print(f"🔔 Update available: {latest_version}")

            data["url"] = f"{BASE_SERVER_URL}{data['url']}"
            if window:
                try:
                    # Send JSON object to frontend JS
                    window.evaluate_js(f"window.onUpdateAvailable({json.dumps(data)});")
                except Exception as e:
                    print("⚠️ Could not notify frontend:", e)
            return data
        else:
            print("✅ App is up to date")
            return None

    except Exception as e:
        print("❌ Update check failed:", e)
        return None


def start_update_checker(window, interval=3600):
    """Background loop to check every X seconds."""

    def run():
        while True:
            print("Starting check for the updates")
            check_for_updates(window)
            time.sleep(interval)

    threading.Thread(target=run, daemon=True).start()


def run_updater(download_url: str):
    try:
        local_filename = os.path.join(
            tempfile.gettempdir(), os.path.basename(download_url)
        )
        print(f"⬇️ Downloading update from {download_url} to {local_filename}")

        with requests.get(download_url, stream=True, timeout=30) as r:
            r.raise_for_status()
            with open(local_filename, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

        print("✅ Download complete, launching installer...")

        if sys.platform.startswith("win"):
            # Run installer and wait for it to complete
            proc = subprocess.Popen([local_filename, "/VERYSILENT", "/NORESTART"])
            proc.wait()  # block until installer exits

            # Relaunch this app (same entrypoint)
            print("🔄 Restarting app...")
            exe_path = sys.executable  # current Python exe or frozen exe
            subprocess.Popen([exe_path] + sys.argv)

        elif sys.platform.startswith("darwin"):
            subprocess.Popen(["open", local_filename])
        else:  # Linux
            subprocess.Popen(["chmod", "+x", local_filename])
            subprocess.Popen([local_filename])

        print("⚡ Exiting app to allow update...")
        os._exit(0)

    except Exception as e:
        print("❌ Update failed:", e)
        return None
