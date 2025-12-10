import asyncio
from pathlib import Path
from typing import Dict, Any
from enum import Enum
import os
import subprocess
import sys
import shutil
import os
import json
import re
import shutil
import zipfile
import tempfile
import requests
from pathlib import Path
from core.utils import get_app_dir, get_mcu_by_board_name


ARDUINO_TEMPLATE = (
    Path(__file__).resolve().parent.parent
    / "core"
    / "transpiler"
    / "runtime"
    / "starter_template"
)


class SessionPhase(str, Enum):
    BEGIN_TRANSPILE = "begin_transpile"
    END_TRANSPILE = "end_transpile"
    BEGIN_COMPILE = "begin_compile"
    END_COMPILE = "end_compile"
    START_UPLOAD = "start_upload"
    END_UPLOAD = "end_upload"
    ALL_DONE = "all_done"
    ERROR = "error"
    CANCELLED = "cancelled"


#############################################################################################################################


import os
import json
import subprocess


def idf_is_installed(env):
    """
    Check whether ESP-IDF is fully installed in the given environment.
    """
    # Basic folder checks
    if not os.path.isdir(env["idf_path"]):
        return False
    if not os.path.isdir(env["idf_tools_path"]):
        return False
    if not os.path.isdir(env["python_env"]):
        return False

    # Check key files
    if not os.path.isfile(env["export_script"]):
        return False
    if not os.path.isfile(env["idf_py"]):
        return False

    # Check python executable
    python_exe = (
        os.path.join(env["python_env"], "python.exe")
        if os.name == "nt"
        else os.path.join(env["python_env"], "bin", "python")
    )
    if not os.path.isfile(python_exe):
        return False

    return True


def setup_idf_env(app_dir):
    """
    Prepare and return the ESP-IDF environment paths.
    Installs ESP-IDF if not already present.
    """
    # Setup folder structure
    idf_root = os.path.join(app_dir, ".mojoscale_idf")
    os.makedirs(idf_root, exist_ok=True)

    metadata_file = os.path.join(idf_root, "idf-env.json")

    # Load existing installation if valid
    if os.path.exists(metadata_file):
        with open(metadata_file, "r") as f:
            data = json.load(f)
            data["idf_root"] = idf_root
            data["metadata_file"] = metadata_file
            if idf_is_installed(data):
                return data

    # Define paths
    idf_path = os.path.join(idf_root, "esp-idf")
    idf_tools_path = os.path.join(idf_root, "tools")
    python_env = os.path.join(idf_root, "python_env")
    export_script = os.path.join(
        idf_path, "export.bat" if os.name == "nt" else "export.sh"
    )
    idf_py = os.path.join(idf_path, "tools", "idf.py")

    data = {
        "idf_root": idf_root,
        "idf_path": idf_path,
        "idf_tools_path": idf_tools_path,
        "python_env": python_env,
        "export_script": export_script,
        "idf_py": idf_py,
        "metadata_file": metadata_file,
    }

    # Install ESP-IDF if missing
    if not idf_is_installed(data):
        # Clone repository
        if not os.path.exists(idf_path):
            subprocess.run(
                [
                    "git",
                    "clone",
                    "--recursive",
                    "https://github.com/espressif/esp-idf.git",
                    idf_path,
                ],
                check=False,
                capture_output=True,
            )

        # Run installation
        env_vars = os.environ.copy()
        env_vars["IDF_TOOLS_PATH"] = idf_tools_path

        install_script = os.path.join(
            idf_path, "install.bat" if os.name == "nt" else "install.sh"
        )
        if os.path.exists(install_script):
            subprocess.run(
                [install_script],
                env=env_vars,
                cwd=idf_path,
                check=False,
                capture_output=True,
            )

    # Save metadata
    with open(metadata_file, "w") as f:
        json.dump(data, f, indent=4)

    return data


import subprocess
import shutil
from pathlib import Path


def create_espidf_project(path, project_id):
    """
    Create an ESP-IDF project with arduino-esp32 and esp-dl components.

    Args:
        path (str): Base path where espidf_projects folder should be
        project_id (str): Name of the project folder

    Returns:
        dict: Status dictionary with 'success', 'message', and 'project_path' keys
    """

    # Convert to Path objects for better path handling
    base_path = Path(path)
    projects_dir = base_path / "espidf_projects"
    project_dir = projects_dir / project_id

    try:
        # Create projects directory if it doesn't exist
        projects_dir.mkdir(parents=True, exist_ok=True)

        # Check if project directory exists
        project_exists = project_dir.exists() and project_dir.is_dir()

        if project_exists:
            print(f"Project '{project_id}' already exists at {project_dir}")
            print("Checking components...")
        else:
            print(f"Creating new ESP-IDF project: {project_id}")
            project_dir.mkdir(parents=True, exist_ok=True)
            create_project_structure(project_dir)

        # Always install/check components
        install_components(project_dir)

        # Always try to install IDF tools (if this function exists)
        try:
            install_idf_tools(project_dir)
        except NameError:
            print("Note: install_idf_tools function not found, skipping...")

        return {
            "success": True,
            "message": f"Project '{project_id}' created/verified successfully",
            "project_path": str(project_dir),
        }

    except Exception as e:
        return {
            "success": False,
            "message": f"Error: {str(e)}",
            "project_path": str(project_dir) if "project_dir" in locals() else None,
        }


def create_project_structure(project_dir):
    """Create basic ESP-IDF project structure"""
    print(f"Creating project structure in {project_dir}")

    # Create main directories
    (project_dir / "main").mkdir(exist_ok=True)
    (project_dir / "components").mkdir(exist_ok=True)

    # Create main CMakeLists.txt
    main_cmake = project_dir / "CMakeLists.txt"
    if not main_cmake.exists():
        main_cmake.write_text(
            f"""
cmake_minimum_required(VERSION 3.16)
include($ENV{IDF_PATH}/tools/cmake/project.cmake)

set(EXTRA_COMPONENT_DIRS
    "${CMAKE_SOURCE_DIR}/components"
    "${CMAKE_SOURCE_DIR}/components_auto"
    ${MANAGED_COMPS}
)
project({project_id})
"""
        )

    # Create main CMakeLists.txt
    main_dir_cmake = project_dir / "main" / "CMakeLists.txt"
    if not main_dir_cmake.exists():
        main_dir_cmake.write_text(
            """
#
# AUTO-DISCOVER AND REQUIRE *ALL* COMPONENTS
#

# FOLDERS YOU WANT TO INCLUDE
set(COMP_DIRS
    "${CMAKE_SOURCE_DIR}/components"
    "${CMAKE_SOURCE_DIR}/components_auto"
    "${CMAKE_SOURCE_DIR}/managed_components"
)

set(ALL_COMPONENT_NAMES "")

foreach(dir ${COMP_DIRS})
    if(EXISTS "${dir}")
        file(GLOB children "${dir}/*")

        foreach(path ${children})
            if(IS_DIRECTORY "${path}")
                get_filename_component(comp "${path}" NAME)
                list(APPEND ALL_COMPONENT_NAMES "${comp}")
            endif()
        endforeach()
    endif()
endforeach()

# Remove the "main" component from the list (cannot depend on itself)
list(REMOVE_ITEM ALL_COMPONENT_NAMES "main")



idf_component_register(SRCS "main.cpp" "arduino_code.cpp"
                    INCLUDE_DIRS "."
                    REQUIRES ${ALL_COMPONENT_NAMES})

"""
        )

    # Create main.cpp
    main_cpp = project_dir / "main" / "main.cpp"
    if not main_cpp.exists():
        main_cpp.write_text(
            """
#include "Arduino.h"

// Forward declarations if they're in another file
extern void setup();
extern void loop();

extern "C" void app_main() {
    initArduino();
    
    // Call Arduino setup()
    setup();
    
    // Call Arduino loop() forever
    while (true) {
        loop();
        // Optional: Add small delay or yield
        delay(1);  // or vTaskDelay(1 / portTICK_PERIOD_MS)
    }
}
"""
        )

    # Create sdkconfig.defaults
    sdkconfig_defaults = project_dir / "sdkconfig.defaults"
    if not sdkconfig_defaults.exists():
        sdkconfig_defaults.write_text(
            """
# Enable Arduino as a component
CONFIG_ARDUINO_ENABLED=y

# Enable C++ exceptions
CONFIG_COMPILER_CXX_EXCEPTIONS=y

# Set WiFi as station mode
CONFIG_ESP_WIFI_STA_TASK_PRIO=5
CONFIG_ESP_WIFI_TASK_PINNED_TO_CORE_0=y

# Increase main stack size for Arduino
CONFIG_ESP_MAIN_TASK_STACK_SIZE=3584

# Enable SPI RAM if available
CONFIG_SPIRAM_SUPPORT=y
CONFIG_SPIRAM_USE_CAPS_ALLOC=y
CONFIG_FREERTOS_HZ=1000

CONFIG_ESP_LOG_WRAPPERS=y


CONFIG_PARTITION_TABLE_CUSTOM=y
CONFIG_PARTITION_TABLE_CUSTOM_FILENAME="partitions.csv"
CONFIG_PARTITION_TABLE_SINGLE_APP=n
CONFIG_ESPTOOLPY_FLASHSIZE_2MB=n
CONFIG_ESPTOOLPY_FLASHSIZE_4MB=y

"""
        )

    print("✓ Project structure created")


import subprocess
import shutil
from pathlib import Path


def install_components(project_dir):
    """Install arduino-esp32 and esp-dl components"""

    components_dir = project_dir / "components"
    components_dir.mkdir(exist_ok=True)  # Ensure components directory exists

    print(f"Installing components to: {components_dir}")

    # Install arduino-esp32 component (clone directly as-is)
    arduino_url = "https://github.com/espressif/arduino-esp32.git"
    arduino_dir = components_dir / "arduino-esp32"

    if arduino_dir.exists():
        print("✓ arduino-esp32 already exists")
    else:
        print("Cloning arduino-esp32...")
        try:
            subprocess.run(
                ["git", "clone", "--recursive", arduino_url, str(arduino_dir)],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            print("✓ arduino-esp32 installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"✗ Failed to clone arduino-esp32: {e}")
            if e.stderr:
                print(f"Error details: {e.stderr}")
            raise

    # Install esp-dl component - extract inner esp-dl folder from repo
    esp_dl_url = "https://github.com/espressif/esp-dl.git"
    esp_dl_target_dir = (
        components_dir / "esp-dl"
    )  # This will contain the inner esp-dl folder contents

    # Check if esp-dl already exists with correct structure
    # We want: components/esp-dl/ (with inner folder contents)
    if esp_dl_target_dir.exists() and any(esp_dl_target_dir.iterdir()):
        # Check if it has component.mk or CMakeLists.txt to verify it's valid
        has_valid_files = any(
            esp_dl_target_dir.glob("CMakeLists.txt")
            or esp_dl_target_dir.glob("component.mk")
            or esp_dl_target_dir.glob("include/")
        )
        if has_valid_files:
            print("✓ esp-dl already exists with correct structure")
            return
        else:
            print("⚠ esp-dl exists but appears empty/corrupt, reinstalling...")
            shutil.rmtree(esp_dl_target_dir)

    print("Installing esp-dl with correct structure...")

    # Create temp directory for cloning
    temp_dir = project_dir / "temp_esp_dl"
    if temp_dir.exists():
        shutil.rmtree(temp_dir)

    try:
        print(f"Cloning esp-dl repository...")
        subprocess.run(
            ["git", "clone", "--depth", "1", esp_dl_url, str(temp_dir)],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        # Create the target directory
        esp_dl_target_dir.mkdir(parents=True, exist_ok=True)

        # Look for the inner esp-dl folder in the cloned repo
        # The structure in the repo is: esp-dl/esp-dl/
        source_inner_esp_dl = temp_dir / "esp-dl"

        if source_inner_esp_dl.exists() and source_inner_esp_dl.is_dir():
            print("Found esp-dl folder in repository...")

            # Check if there's another esp-dl folder inside (nested structure)
            nested_inner = source_inner_esp_dl / "esp-dl"
            if nested_inner.exists() and nested_inner.is_dir():
                # Use the deeply nested folder contents
                print(f"Copying contents from deeply nested esp-dl folder...")
                # Copy all contents from the nested folder
                for item in nested_inner.iterdir():
                    if item.name != ".git":
                        dest = esp_dl_target_dir / item.name
                        if item.is_dir():
                            shutil.copytree(item, dest, dirs_exist_ok=True)
                        else:
                            shutil.copy2(item, dest)
            else:
                # Use the folder directly (copy all contents)
                print(f"Copying contents from esp-dl folder...")
                for item in source_inner_esp_dl.iterdir():
                    if item.name != ".git":
                        dest = esp_dl_target_dir / item.name
                        if item.is_dir():
                            shutil.copytree(item, dest, dirs_exist_ok=True)
                        else:
                            shutil.copy2(item, dest)
        else:
            # If the expected structure isn't found, copy everything from root
            print(
                "Expected folder structure not found, copying all repository contents..."
            )
            for item in temp_dir.iterdir():
                if item.name != ".git":
                    dest = esp_dl_target_dir / item.name
                    if item.is_dir():
                        shutil.copytree(item, dest, dirs_exist_ok=True)
                    else:
                        shutil.copy2(item, dest)

        # Create/update CMakeLists.txt if needed
        cmake_file = esp_dl_target_dir / "CMakeLists.txt"
        if not cmake_file.exists():
            cmake_file.write_text(
                """# ESP-DL component
idf_component_register()
"""
            )

        print(
            "✓ esp-dl installed with correct structure (contents directly in components/esp-dl/)"
        )

    except Exception as e:
        print(f"✗ Failed to install esp-dl: {e}")
        # Clean up on error
        if esp_dl_target_dir.exists():
            shutil.rmtree(esp_dl_target_dir)
        raise
    finally:
        # Clean up temp directory
        if temp_dir.exists():
            shutil.rmtree(temp_dir)

    print("✓ All components installed successfully")


# If you have an install_idf_tools function, include it here
def install_idf_tools(project_dir):
    """Placeholder for IDF tools installation if needed"""
    print("Note: IDF tools installation would happen here")
    # Your existing install_idf_tools implementation would go here
    pass


##############################################################################################################################


def merge_arduino_includes_into_idf(build_dir: Path, STARTER_TEMPLATE_ARDUINO: Path):
    """
    Copy all header files (.h / .hpp) from:
        STARTER_TEMPLATE_ARDUINO/include/

    Into:
        build_dir/components/mojoscale_arduino/include/

    Also creates:
        - CMakeLists.txt
        - dummy.cpp
    """

    src_include = STARTER_TEMPLATE_ARDUINO / "include"

    mojoscale_arduino_dir = build_dir / "components" / "mojoscale_arduino"
    dst_include = mojoscale_arduino_dir / "include"

    # Ensure the component directory exists
    mojoscale_arduino_dir.mkdir(parents=True, exist_ok=True)

    # Clean old include directory
    if dst_include.exists():
        shutil.rmtree(dst_include)

    # Recreate include directory
    dst_include.mkdir(parents=True, exist_ok=True)

    # --- WRITE CMakeLists.txt ---
    cmk = mojoscale_arduino_dir / "CMakeLists.txt"
    cmk.write_text(
        """
idf_component_register(
    SRCS "dummy.cpp"
    INCLUDE_DIRS "include"
    REQUIRES arduino-esp32 ArduinoJson esp-dl
)
""".strip()
    )

    # --- WRITE dummy.cpp ---
    dummy = mojoscale_arduino_dir / "dummy.cpp"
    dummy.write_text(
        """
// Empty dummy source file so ESP-IDF recognizes this component.
extern "C" void mojoscale_component_dummy_placeholder() {}
"""
    )

    # --- COPY HEADERS ---
    if not src_include.exists():
        print(f"⚠️ No include/ folder found at {src_include}")
        return

    print("📥 Copying Arduino include → ESP-IDF mojoscale_arduino/include/")
    for file in src_include.rglob("*"):
        if file.is_file() and file.suffix.lower() in [".h", ".hpp"]:
            rel = file.relative_to(src_include)
            target = dst_include / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(file, target)
            print(f"   → {target}")


def convert_arduino_libs_to_idf_components(
    build_dir: Path, STARTER_TEMPLATE_ARDUINO: Path
):
    """
    Convert Arduino libraries in:
        STARTER_TEMPLATE_ARDUINO/lib/<LibName>/

    Into ESP-IDF components placed at:
        build_dir/components/auto_libs/<LibName>/

    This folder is fully wiped and regenerated every run.
    Each library becomes its own ESP-IDF component containing:
        - The copied library source files
        - An auto-generated CMakeLists.txt
    """

    libs_dir = STARTER_TEMPLATE_ARDUINO / "lib"
    auto_libs = build_dir / "components_auto"

    # Wipe any previous generated components
    if auto_libs.exists():
        shutil.rmtree(auto_libs)
    auto_libs.mkdir(parents=True, exist_ok=True)

    if not libs_dir.exists():
        print(f"⚠️ No Arduino lib/ folder found at {libs_dir}")
        return

    print("📦 Rebuilding Arduino libs → ESP-IDF components/auto_libs/")

    for lib in libs_dir.iterdir():
        allowed_libs = ["BLESimple", "NimBLESimple", "PedestrianDetector"]
        if not lib.is_dir() or lib.name not in allowed_libs:
            continue

        comp = auto_libs / lib.name
        shutil.copytree(lib, comp, dirs_exist_ok=True)

        sources = []
        includes = set()

        # Collect source files
        for src in comp.rglob("*.c"):
            sources.append(str(src.relative_to(comp)).replace("\\", "/"))
        for src in comp.rglob("*.cpp"):
            sources.append(str(src.relative_to(comp)).replace("\\", "/"))

        # Collect include directories
        for h in list(comp.rglob("*.h")) + list(comp.rglob("*.hpp")):
            rel = str(h.parent.relative_to(comp)).replace("\\", "/")
            if rel != ".":
                includes.add(rel)

        include_dirs = " ".join(f'"{x}"' for x in sorted(includes)) or "."

        # Create component CMakeLists
        cmk = comp / "CMakeLists.txt"
        cmk.write_text(
            f"""
idf_component_register(
    SRCS {" ".join(f'"{s}"' for s in sources)}
    INCLUDE_DIRS {include_dirs}
    REQUIRES arduino-esp32 esp-dl
)
"""
        )

        print(f"   ✔ Component created: {comp}")


##################################################################################################################################


import requests
import tempfile
import zipfile
import os
import shutil
from pathlib import Path


def download_and_extract_zip(url: str, dest: Path) -> Path:
    """Download and extract zip, returning the root directory with library contents."""
    resp = requests.get(url, stream=True, timeout=30)
    resp.raise_for_status()

    with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as tmp:
        for chunk in resp.iter_content(chunk_size=8192):
            if chunk:
                tmp.write(chunk)
        tmp_path = tmp.name

    try:
        with zipfile.ZipFile(tmp_path, "r") as zip_ref:
            # Extract to temp location first to handle nested directories
            temp_extract = dest / "_temp_extract"
            if temp_extract.exists():
                shutil.rmtree(temp_extract)
            temp_extract.mkdir(parents=True, exist_ok=True)
            zip_ref.extractall(temp_extract)

        # Find the actual library root
        extracted_items = list(temp_extract.iterdir())

        if not extracted_items:
            raise RuntimeError(f"Empty archive from {url}")

        # PlatformIO archives often have the library directly in the zip
        # GitHub archives have a single directory with branch name
        root = None

        # Check for common PlatformIO structure
        possible_roots = []
        for item in extracted_items:
            if item.is_dir():
                # Look for library.properties or library.json in PlatformIO libs
                if (item / "library.properties").exists() or (
                    item / "library.json"
                ).exists():
                    possible_roots.append(item)
                elif (item / "src").exists() or (item / "include").exists():
                    possible_roots.append(item)
                elif any(item.glob("*.h")) or any(item.glob("*.cpp")):
                    possible_roots.append(item)

        if possible_roots:
            # Move the most likely candidate
            root_candidate = possible_roots[0]
            # Move contents to dest
            for item in root_candidate.iterdir():
                shutil.move(str(item), str(dest / item.name))
            if len(possible_roots) == 1 and len(extracted_items) == 1:
                # Single directory, clean up
                shutil.rmtree(temp_extract)
                root = dest
        else:
            # Move everything to dest
            for item in extracted_items:
                shutil.move(str(item), str(dest / item.name))
            shutil.rmtree(temp_extract)
            root = dest

        # Clean up zip file
        os.unlink(tmp_path)

        if root is None:
            root = dest

        return root

    except Exception as e:
        # Cleanup on error
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
        if temp_extract.exists():
            shutil.rmtree(temp_extract, ignore_errors=True)
        raise


def install_dependencies(dependencies: list[str], build_dir: Path):
    """Install dependencies - SIMPLE VERSION"""
    import json

    components_auto = build_dir / "components_auto"
    components_auto.mkdir(exist_ok=True)

    for dep in dependencies:
        print(f"📦 Processing: {dep}")

        # 1. Download the thing
        if dep.startswith("http"):
            # GitHub URL
            if "github.com" in dep:
                repo_name = dep.rstrip("/").split("/")[-1].replace(".git", "")
                lib_name = repo_name
                author = dep.rstrip("/").split("/")[-2]

                # Try main then master
                for branch in ["main", "master"]:
                    try:
                        clean_url = dep.replace(".git", "").rstrip("/")
                        url = f"{clean_url}/archive/refs/heads/{branch}.zip"
                        root = download_and_extract_zip(url, components_auto / lib_name)
                        if root:
                            print(f"   ✓ Downloaded from GitHub ({branch})")
                            break
                    except:
                        continue
            else:
                raise ValueError(f"Unsupported URL: {dep}")
        else:
            # PlatformIO format: author/library@version
            parts = dep.split("@")
            author_lib = parts[0]
            author, lib_name = author_lib.split("/")
            version = parts[1] if len(parts) > 1 else None

            # Try PlatformIO registry
            try:
                pio_url = f"https://api.registry.platformio.org/v3/lib/download/{author}/{lib_name}"
                if version:
                    pio_url += f"?version={version}"
                root = download_and_extract_zip(pio_url, components_auto / lib_name)
                print(f"   ✓ Downloaded from PlatformIO")
            except:
                # Fallback to GitHub
                for branch in ["main", "master"]:
                    try:
                        url = f"https://github.com/{author}/{lib_name}/archive/refs/heads/{branch}.zip"
                        root = download_and_extract_zip(url, components_auto / lib_name)
                        if root:
                            print(f"   ✓ Downloaded from GitHub ({branch})")
                            break
                    except:
                        continue

        if not root:
            print(f"   ❌ Failed to download: {dep}")
            continue

        # 2. Check for CMakeLists.txt - if not exists, create simple one
        cmake_file = root / "CMakeLists.txt"
        if not cmake_file.exists():
            print(f"   📄 Creating minimal CMakeLists.txt")

            # Simple CMakeLists.txt
            cmake_content = f"""idf_component_register(
    COMPONENT_NAME {lib_name}
    INCLUDE_DIRS "."
"""

            # Add arduino requirement for Arduino libraries
            is_arduino_lib = (
                (root / "library.properties").exists()
                or (root / "library.json").exists()
                or "arduino" in lib_name.lower()
            )

            if is_arduino_lib:
                cmake_content += "    REQUIRES arduino-esp32\n"

            # Add esp-dl requirement for esp-dl library
            if "esp-dl" in lib_name.lower():
                cmake_content += "    REQUIRES esp-dl\n"

            cmake_content += ")"

            cmake_file.write_text(cmake_content)
        else:
            print(f"   📄 Using existing CMakeLists.txt")

        print(f"   ✔ Installed: {lib_name}")

    print(f"\n✅ All dependencies installed to: {components_auto}")


# ============================================================================
# WRITE TRANSPILER OUTPUT
# ============================================================================
def write_transpiled_code(files: dict, build_dir: Path):
    src_dir = build_dir / "main"
    include_dir = build_dir / "components" / "mojoscale_arduino" / "include"

    src_dir.mkdir(parents=True, exist_ok=True)
    include_dir.mkdir(parents=True, exist_ok=True)

    for name, code in files.items():
        if name == "main.py":
            out = src_dir / "arduino_code.cpp"
        else:
            out = include_dir / name.replace(".py", ".h")
        out.write_text(code, encoding="utf-8")
        print(f"✍️ Wrote {out}")


################################################################################################################################


import asyncio
import os
from pathlib import Path


import asyncio
import os
from pathlib import Path


async def compile_espidf_project(
    build_path: Path, idf_env: dict, target: str = "esp32"
):
    """
    Strict ESP-IDF compiler that:
    1. Verifies python environment
    2. If missing, runs ESP-IDF installer automatically
    3. Compiles the project using bundled idf.py
    """

    # ---------------------------
    # Validate project folder
    # ---------------------------
    if not build_path.exists():
        return {
            "success": False,
            "error": f"Project folder does not exist: {build_path}",
        }

    # Resolve required paths
    idf_path = idf_env["idf_path"]
    python_env = idf_env["python_env"]
    idf_py = idf_env["idf_py"]

    # Determine python executable path
    if os.name == "nt":
        python_exe = os.path.join(python_env, "python.exe")
        install_script = os.path.join(idf_path, "install.bat")
    else:
        python_exe = os.path.join(python_env, "bin", "python")
        install_script = os.path.join(idf_path, "install.sh")

    # ---------------------------
    # Step 1: Ensure python environment exists
    # ---------------------------
    if not os.path.isfile(python_exe):
        # Run ESP-IDF installer automatically
        if not os.path.isfile(install_script):
            return {
                "success": False,
                "error": f"ESP-IDF install script not found: {install_script}",
            }

        try:
            # Run install.bat or install.sh in blocking mode
            proc = await asyncio.create_subprocess_exec(
                install_script,
                cwd=idf_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            out, err = await proc.communicate()
            out, err = out.decode(), err.decode()

            if proc.returncode != 0:
                return {
                    "success": False,
                    "error": (
                        "ESP-IDF install script failed.\n"
                        f"Script: {install_script}\n"
                        f"Return code: {proc.returncode}\n"
                        f"Output:\n{err or out}"
                    ),
                }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to run ESP-IDF installer: {str(e)}",
            }

        # Re-check python environment after install
        if not os.path.isfile(python_exe):
            return {
                "success": False,
                "error": (
                    "ESP-IDF python environment still missing after installer run.\n"
                    f"Expected python at: {python_exe}"
                ),
            }

    # ---------------------------
    # Step 2: Ensure idf.py exists
    # ---------------------------
    if not os.path.isfile(idf_py):
        return {
            "success": False,
            "error": f"idf.py not found at expected location: {idf_py}",
        }

    # ---------------------------
    # Step 3: Prepare environment variables
    # ---------------------------
    env = os.environ.copy()
    env["IDF_PATH"] = idf_path
    env["IDF_TOOLS_PATH"] = idf_env["idf_tools_path"]
    env["IDF_TARGET"] = target

    # ---------------------------
    # Step 4: Build command
    # ---------------------------
    cmd = [python_exe, idf_py, "build"]

    # ---------------------------
    # Step 5: Run compilation
    # ---------------------------
    try:
        process = await asyncio.create_subprocess_exec(
            *cmd,
            cwd=str(build_path),
            env=env,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        stdout, stderr = await process.communicate()
        stdout = stdout.decode(errors="replace") if stdout else ""
        stderr = stderr.decode(errors="replace") if stderr else ""

        if process.returncode != 0:
            return {
                "success": False,
                "error": stderr.strip() or "Unknown ESP-IDF compile error",
                "stdout": stdout,
                "stderr": stderr,
                "returncode": process.returncode,
                "cmd": " ".join(cmd),
            }

        return {
            "success": True,
            "stdout": stdout,
            "stderr": stderr,
            "build_path": str(build_path),
            "returncode": 0,
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"Compilation process failed: {str(e)}",
            "stdout": "",
            "stderr": "",
            "returncode": -1,
        }


async def compile_and_upload_espidf_project(
    build_path: Path,
    idf_env: dict,
    port: str,
    target: str = "esp32",
    baud: int = 460800,
):
    """
    Compile, then upload firmware using private ESP-IDF env.
    """

    # Step 1: Compile
    result = await compile_espidf_project(build_path, idf_env, target)
    if not result["success"]:
        return {
            "success": False,
            "compile_success": False,
            "upload_success": False,
            "error": result["error"],
        }

    # Resolve paths
    if os.name == "nt":
        python_exe = os.path.join(idf_env["python_env"], "python.exe")
    else:
        python_exe = os.path.join(idf_env["python_env"], "bin", "python")

    idf_py = idf_env["idf_py"]

    # Prepare env
    env = os.environ.copy()
    env["IDF_PATH"] = idf_env["idf_path"]
    env["IDF_TOOLS_PATH"] = idf_env["idf_tools_path"]
    env["IDF_TARGET"] = target

    # Upload command
    cmd = [python_exe, idf_py, "-p", port, "-b", str(baud), "flash"]

    process = await asyncio.create_subprocess_exec(
        *cmd,
        cwd=str(build_path),
        env=env,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    stdout, stderr = await process.communicate()
    stdout, stderr = stdout.decode(), stderr.decode()

    if process.returncode != 0:
        return {
            "success": False,
            "compile_success": True,
            "upload_success": False,
            "error": stderr.strip() or "Upload failed",
            "stdout": stdout,
            "stderr": stderr,
        }

    return {
        "success": True,
        "compile_success": True,
        "upload_success": True,
        "stdout": stdout,
        "stderr": stderr,
        "port": port,
    }


def find_firmware_binary(build_path: Path, target: str) -> str:
    """
    Find the compiled firmware binary

    Args:
        build_path: Path to the ESP-IDF project directory
        target: ESP-IDF target
    """
    # Common binary locations in ESP-IDF build directories
    possible_paths = [
        build_path / "build" / f"{target}.bin",
        build_path / "build" / f"{target}.bootloader.bin",
        build_path / "build" / "firmware.bin",
        build_path / "build" / f"app-template-{target}.bin",
    ]

    for path in possible_paths:
        if path.exists():
            return str(path)

    # Fallback: look for any .bin file in build directory
    build_dir = build_path / "build"
    if build_dir.exists():
        bin_files = list(build_dir.glob("*.bin"))
        if bin_files:
            return str(bin_files[0])

    return None


# ============================================================================
# UPLOAD PORT DETECTION
# ============================================================================
def find_esp_serial_port():
    ports = list(serial.tools.list_ports.comports())
    for p in ports:
        desc = (p.description or "").lower()
        if any(x in desc for x in ["esp", "ch340", "cp210"]):
            return p.device
    return ports[0].device if ports else None


##############################################################################################################################
async def run_espidf_custom_pipeline(
    session,
    project_id: str,
    build_dir: Path,
    transpiled_files: Dict[str, str],
    transpiler_metadata: Dict[str, Any],
    board: str,
    platform: str,
    upload_requested: bool,
):
    """
    SIMPLE PLACEHOLDER:
    This replaces the PlatformIO build+upload path for ESP-IDF.
    Future functionality may:
        - call idf.py build
        - analyze outputs
        - perform direct esptool uploads
        - hook into custom IDF workflows

    For now it simply reports completion.
    """

    await session.send(
        SessionPhase.BEGIN_COMPILE, "ESP-IDF custom pipeline starting..."
    )

    # step 1 create espidf new project or check if it exists

    app_dir = get_app_dir()

    # check if idf exists

    idf_env = setup_idf_env(app_dir)

    build_path = Path(f"{app_dir}/espidf_projects/{project_id}")

    create_espidf_project(app_dir, project_id)
    merge_arduino_includes_into_idf(build_path, ARDUINO_TEMPLATE)
    convert_arduino_libs_to_idf_components(build_path, ARDUINO_TEMPLATE)

    dependencies = transpiler_metadata["dependencies"]
    dependencies.append("bblanchon/ArduinoJson")
    dependencies.append("adafruit/Adafruit_BusIO")
    install_dependencies(dependencies, build_path)

    write_transpiled_code(transpiled_files, build_path)

    # --------------------------------------------------------------------
    # ESP-IDF build system integration
    # --------------------------------------------------------------------

    # Determine chip type from board (you might want to add mapping logic)
    # chip = "esp32"  # Default, adjust based on board parameter
    chip = get_mcu_by_board_name(board)

    if upload_requested:
        # Get port from metadata or environment
        port = find_esp_serial_port()

        # Compile and upload
        result = await compile_and_upload_espidf_project(
            build_path,
            idf_env,
            port,
            target=chip,  # Can be different from chip in some cases
            baud_rate=921600,
        )

        upload_success = result.get("upload_success", False)

        if result["success"]:
            await session.send(
                SessionPhase.ALL_DONE,
                f"ESP-IDF pipeline completed: Compiled and uploaded to {port}",
            )
        else:
            await session.send(
                SessionPhase.BEGIN_COMPILE, f"ESP-IDF pipeline completed with errors"
            )
    else:
        # Just compile
        result = await compile_espidf_project(build_path, idf_env, target=chip)

        upload_success = False

        if result["success"]:
            await session.send(
                SessionPhase.ALL_DONE,
                "ESP-IDF pipeline completed: Compiled successfully",
            )
        else:
            err = result.get("error", "Compilation failed")

            msg = result

            # stderr_lines = result.get("stderr", "").strip().split("\n")
            # last_lines = "\n".join(stderr_lines[-20:]) if stderr_lines else err

            # msg += last_lines

            await session.send(SessionPhase.BEGIN_COMPILE, msg)

    return {
        "success": result.get("success", True),
        "upload_success": upload_success,
        "session_id": session.id,
        "build_dir": str(build_dir),
        "details": result,  # Include detailed results from compile/upload
    }
