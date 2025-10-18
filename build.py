import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path

APP_NAME = "MojoscaleIDE"
ENTRY_FILE = "app.py"
FRONTEND_DIST = Path("frontend") / "dist"
TRANSPILER_DIR = Path("core") / "transpiler"


def run_cmd(cmd):
    print(f">>> {cmd}")
    subprocess.check_call(cmd, shell=True)


def copy_transpiler_files_post_build():
    """
    Manually copy transpiler Python files after build.
    Nuitka 1.4+ filters out .py and .pyi files from data dirs,
    so we copy them manually to the dist folder.
    """
    dist_dir = Path("build") / "app.dist"

    if not dist_dir.exists():
        print(f"⚠️  {dist_dir} not found")
        return False

    success = True

    # Copy core_stubs (*.pyi files)
    stubs_src = TRANSPILER_DIR / "core_stubs"
    stubs_dest = dist_dir / "core" / "transpiler" / "core_stubs"

    if stubs_src.exists():
        try:
            stubs_dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(stubs_src, stubs_dest, dirs_exist_ok=True)
            stub_count = len(list(stubs_src.rglob("*.pyi")))
            print(f"✓ Copied {stub_count} .pyi stub files to {stubs_dest}")
        except Exception as e:
            print(f"✗ Failed to copy core_stubs: {e}")
            success = False
    else:
        print(f"⚠️  {stubs_src} not found")
        success = False

    # Copy core_libs (*.py files)
    libs_src = TRANSPILER_DIR / "core_libs"
    libs_dest = dist_dir / "core" / "transpiler" / "core_libs"

    if libs_src.exists():
        try:
            libs_dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(libs_src, libs_dest, dirs_exist_ok=True)
            py_count = len(list(libs_src.rglob("*.py")))
            print(f"✓ Copied {py_count} .py files to {libs_dest}")
        except Exception as e:
            print(f"✗ Failed to copy core_libs: {e}")
            success = False
    else:
        print(f"⚠️  {libs_src} not found")
        success = False

    return success


def build():
    # Ensure frontend build exists
    if not FRONTEND_DIST.exists():
        print("❌ frontend/dist not found. Run `npm run build` first.")
        sys.exit(1)

    # Check transpiler dirs exist
    if not TRANSPILER_DIR.exists():
        print(f"❌ {TRANSPILER_DIR} not found.")
        sys.exit(1)

    print("=" * 60)
    print("Building MojoscaleIDE with Nuitka")
    print("=" * 60)

    # Common Nuitka options
    options = [
        f"--standalone",
        f"--enable-plugin=tk-inter",
        f"--include-data-dir={FRONTEND_DIST}=frontend/dist",
        f"--output-dir=build",
        f"--include-data-files=core/core_modules_index.json=core/core_modules_index.json",
        f"--include-data-files=core/available_boards.json=core/available_boards.json",
        f"--remove-output",
        f"--assume-yes-for-downloads",
        "--nofollow-import-to=tkinter",
        "--nofollow-import-to=PyQt5",
        "--nofollow-import-to=PySide6",
    ]

    # Include the package so Nuitka knows to process core.transpiler
    options.append("--include-package=core.transpiler.core_libs")

    system = platform.system()

    # Final command
    cmd = f"python -m nuitka {ENTRY_FILE} " + " ".join(options)

    print("\n>>> PHASE 1: Nuitka Compilation\n")
    try:
        run_cmd(cmd)
    except subprocess.CalledProcessError as e:
        print(f"❌ Nuitka compilation failed: {e}")
        sys.exit(1)

    print("\n>>> PHASE 2: Post-Build File Copying\n")
    print("(Copying .py and .pyi files that Nuitka filtered out)\n")

    if copy_transpiler_files_post_build():
        print("\n" + "=" * 60)
        print("✓ Build completed successfully!")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("⚠️  Build completed with warnings (check files above)")
        print("=" * 60)


if __name__ == "__main__":
    build()
