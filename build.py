import os
import sys
import subprocess
import platform
from pathlib import Path

APP_NAME = "MojoscaleIDE"
ENTRY_FILE = "app.py"
FRONTEND_DIST = Path("frontend") / "dist"


def run_cmd(cmd):
    print(f">>> {cmd}")
    subprocess.check_call(cmd, shell=True)


def build():
    # Ensure frontend build exists
    if not FRONTEND_DIST.exists():
        print("❌ frontend/dist not found. Run `npm run build` first.")
        sys.exit(1)

    # Common Nuitka options
    options = [
        f"--standalone",  # make a self-contained bundle
        # f"--onefile",  # single exe (optional, skip for dir bundle)
        f"--enable-plugin=tk-inter",  # needed by pywebview on some GUIs
        f"--include-data-dir={FRONTEND_DIST}=frontend/dist",  # bundle frontend
        f"--output-dir=build",  # build folder
        # f"--include-data-files=*.json=.",  # Root level JSONs
        f"--include-data-files=core/core_modules_index.json=core/core_modules_index.json",  # Core folder JSONs (one level deep)
        f"--remove-output",  # clean old builds
        f"--assume-yes-for-downloads",  # auto download needed files
        "--nofollow-import-to=tkinter",  # avoid tkinter bloat (pywebview may fallback)
        "--nofollow-import-to=PyQt5",  # avoid qt bloat unless needed
        "--nofollow-import-to=PySide6",  # avoid qt bloat unless needed
    ]

    # Platform-specific tweaks
    system = platform.system()
    """if system == "Windows":
        options.append(f"--windows-icon-from-ico=icon.ico")  # add an icon
    elif system == "Darwin":
        options.append(f"--macos-app-icon=icon.icns")
        options.append(f"--macos-create-app-bundle")
    elif system == "Linux":
        pass  # optional: set rpath or other linux tweaks

    """

    # Final command
    cmd = f"python -m nuitka {ENTRY_FILE} " + " ".join(options)
    run_cmd(cmd)


if __name__ == "__main__":
    build()
