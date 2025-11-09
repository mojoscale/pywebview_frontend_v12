import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent
ROOT_DIR = PROJECT_DIR.parent  # one level up
VENV_PATH = ROOT_DIR / ".venv"  # assuming `.venv` folder
print(f"🔍 Project dir: {PROJECT_DIR}")
print(f"🔍 Root dir: {ROOT_DIR}")
print(f"🔍 Venv path: {VENV_PATH}")

# Detect site-packages path
if platform.system() == "Windows":
    SITE_PACKAGES = VENV_PATH / "Lib" / "site-packages"
else:
    pyver = f"python{sys.version_info.major}.{sys.version_info.minor}"
    SITE_PACKAGES = VENV_PATH / "lib" / pyver / "site-packages"

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


def setup_jedi_environment_in_build():
    """
    Setup Jedi environment files in the build directory to prevent
    it from trying to spawn Python subprocesses.
    """
    dist_dir = Path("build") / "app.dist"

    if not dist_dir.exists():
        print(f"⚠️  {dist_dir} not found")
        return False

    try:
        # Create a fake environment info file for Jedi
        jedi_cache_dir = dist_dir / "jedi_cache"
        jedi_cache_dir.mkdir(exist_ok=True)

        # Get current Python version info
        import sys

        version_info = sys.version_info

        # Create environment info that Jedi would normally get by spawning python
        env_info = {
            "version_info": list(version_info),
            "executable": sys.executable,
            "sys_path": sys.path,
        }

        # Write this to a file that our patched Jedi will read
        import json

        env_file = jedi_cache_dir / "environment_info.json"
        with open(env_file, "w") as f:
            json.dump(env_info, f)

        print("✓ Created Jedi environment info file")
        return True

    except Exception as e:
        print(f"❌ Error setting up Jedi environment: {e}")
        return False


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
        f"--include-data-dir=core/transpiler=core/transpiler",
        f"--remove-output",
        f"--assume-yes-for-downloads",
        "--nofollow-import-to=tkinter",
        "--nofollow-import-to=PyQt5",
        "--nofollow-import-to=PySide6",
        # Include packages explicitly
        "--include-package=jedi",
        "--include-package=parso",
        "--include-package=core.transpiler.core_libs",
        # Disable console for Windows TBD
        "--windows-console-mode=disable",
        "--include-package=black",
        "--include-package=pathspec",
        "--include-package=platformdirs",
        "--include-package=typing_extensions",
        f"--include-data-dir={SITE_PACKAGES / 'black'}=black",
        f"--include-data-dir={SITE_PACKAGES / 'pathspec'}=pathspec",
        f"--include-data-dir={SITE_PACKAGES / 'platformdirs'}=platformdirs",
        # f"--include-data-dir={SITE_PACKAGES / 'typing_extensions'}=typing_extensions",
    ]

    # Remove empty strings
    options = [opt for opt in options if opt]

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

    build_success = True

    if not copy_transpiler_files_post_build():
        build_success = False

    print("\n>>> PHASE 3: Setting up Jedi Environment\n")
    if not setup_jedi_environment_in_build():
        build_success = False

    if build_success:
        print("\n" + "=" * 60)
        print("✓ Build completed successfully!")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("⚠️  Build completed with warnings (check files above)")
        print("=" * 60)


if __name__ == "__main__":
    build()
