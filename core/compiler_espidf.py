import asyncio
from pathlib import Path
from typing import Dict, Any
from enum import Enum
import os
import subprocess
import sys
import shutil
import os
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

        # Check if project already exists
        if project_dir.exists() and project_dir.is_dir():
            print(f"Project '{project_id}' already exists at {project_dir}")
            print("Checking components...")

            # Check for required components
            components_dir = project_dir / "components"
            arduino_esp32_dir = components_dir / "arduino-esp32"
            esp_dl_dir = components_dir / "esp-dl"

            components_status = {
                "arduino-esp32": arduino_esp32_dir.exists()
                and arduino_esp32_dir.is_dir(),
                "esp-dl": esp_dl_dir.exists() and esp_dl_dir.is_dir(),
            }

            if all(components_status.values()):
                print("All components are already installed.")
                return {
                    "success": True,
                    "message": f"Project '{project_id}' already exists with all components",
                    "project_path": str(project_dir),
                    "components_installed": components_status,
                }
            else:
                print("Some components are missing. Installing missing components...")
                # Continue to installation
        else:
            print(f"Creating new ESP-IDF project: {project_id}")
            project_dir.mkdir(parents=True, exist_ok=True)
            create_project_structure(project_dir)

        # Install components
        print("Installing components...")
        install_components(project_dir)

        return {
            "success": True,
            "message": f"Project '{project_id}' created successfully",
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

    # Create main directory with main.cpp
    main_dir = project_dir / "main"
    main_dir.mkdir(exist_ok=True)

    # Create main.cpp with basic template
    main_cpp_content = """

#include "Arduino.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

void setup();
void loop();

void arduinoTask(void *pvParameters) {
    setup();
    while(1) {
        loop();
        taskYIELD(); // Yield to other tasks
    }
}

extern "C" void app_main()
{
    initArduino();
    
    // Create task for Arduino code
    xTaskCreatePinnedToCore(
        arduinoTask,    // Task function
        "ArduinoTask",  // Task name
        8192,           // Stack size
        NULL,           // Parameters
        1,              // Priority
        NULL,           // Task handle
        0               // Core (0 or 1)
    );
    
    // Your ESP-IDF code can continue here
    while(true) {
        // ESP-IDF specific code
        vTaskDelay(1000 / portTICK_PERIOD_MS);
    }
}


"""

    (main_dir / "main.cpp").write_text(main_cpp_content)

    # Create CMakeLists.txt for main
    main_cmake_content = """idf_component_register(SRCS "main.cpp" "arduino_code.cpp"
                    INCLUDE_DIRS ".")
"""
    (main_dir / "CMakeLists.txt").write_text(main_cmake_content)

    # Create project root CMakeLists.txt
    root_cmake_content = (
        """cmake_minimum_required(VERSION 3.16)
include($ENV{IDF_PATH}/tools/cmake/project.cmake)

set(EXTRA_COMPONENT_DIRS
    "${CMAKE_SOURCE_DIR}/components"
    "${CMAKE_SOURCE_DIR}/components_auto"
    ${MANAGED_COMPS}
)
project(%s)
"""
        % project_dir.name
    )

    (project_dir / "CMakeLists.txt").write_text(root_cmake_content)

    # Create components directory
    components_dir = project_dir / "components"
    components_dir.mkdir(exist_ok=True)

    # Create sdkconfig.defaults with common settings
    sdkconfig_content = """# Enable Arduino as a component
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
"""

    (project_dir / "sdkconfig.defaults").write_text(sdkconfig_content)

    print(f"Created basic project structure at {project_dir}")


def install_components(project_dir):
    """Install arduino-esp32 and esp-dl components"""

    components_dir = project_dir / "components"

    # Clone arduino-esp32 component
    arduino_url = "https://github.com/espressif/arduino-esp32.git"
    arduino_dir = components_dir / "arduino-esp32"

    if not arduino_dir.exists():
        print("Cloning arduino-esp32...")
        subprocess.run(
            ["git", "clone", "--recursive", arduino_url, str(arduino_dir)],
            check=True,
            capture_output=True,
            text=True,
        )
        print("✓ arduino-esp32 installed")
    else:
        print("✓ arduino-esp32 already exists")

    # Clone esp-dl component
    esp_dl_url = "https://github.com/espressif/esp-dl.git"
    esp_dl_dir = components_dir / "esp-dl"

    if not esp_dl_dir.exists():
        print("Cloning esp-dl...")
        subprocess.run(
            ["git", "clone", "--recursive", esp_dl_url, str(esp_dl_dir)],
            check=True,
            capture_output=True,
            text=True,
        )
        print("✓ esp-dl installed")
    else:
        print("✓ esp-dl already exists")

    # Create component CMakeLists.txt if needed
    for component in ["arduino-esp32", "esp-dl"]:
        component_dir = components_dir / component
        cmake_file = component_dir / "CMakeLists.txt"

        if not cmake_file.exists():
            # Create a simple CMakeLists.txt to register the component
            cmake_content = """# Register component
idf_component_register()
"""
            cmake_file.write_text(cmake_content)


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
    REQUIRES arduino-esp32
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
    REQUIRES arduino-esp32
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


def install_dependencies(
    dependencies: list[str], build_dir: Path, already_installed=None, depth=0
):
    """Install dependencies with nested dependency resolution."""
    import json
    import re

    components_auto = build_dir / "components_auto"
    components_auto.mkdir(exist_ok=True)

    # Track installed dependencies to avoid cycles
    if already_installed is None:
        already_installed = set()

    indent = "   " * depth

    # Process each dependency
    for dep in dependencies:
        print(f"{indent}📦 Processing: {dep}")

        # Parse dependency spec
        if dep.startswith("http"):
            if "github.com" in dep:
                repo_name = dep.rstrip("/").split("/")[-1].replace(".git", "")
                lib_name = repo_name
                author = dep.rstrip("/").split("/")[-2]
                version = None
            else:
                raise ValueError(f"Unsupported URL format: {dep}")
        else:
            # Parse PlatformIO format: author/library@version or author/library
            parts = dep.split("@")
            author_lib = parts[0]
            author, lib_name = author_lib.split("/")
            version = parts[1] if len(parts) > 1 else None

        # Create unique key for tracking
        dep_key = f"{author}/{lib_name}"
        if version:
            dep_key += f"@{version}"

        # Skip if already installed at this exact version
        if dep_key in already_installed:
            print(f"{indent}   ⏭️ Already installed: {lib_name}")
            continue

        already_installed.add(dep_key)
        target_dir = components_auto / lib_name

        # Clean existing if different version
        if target_dir.exists():
            shutil.rmtree(target_dir)
        target_dir.mkdir(parents=True, exist_ok=True)

        # Download and extract
        root = None
        if dep.startswith("http"):
            # GitHub URL
            for branch in ["main", "master"]:
                try:
                    clean_url = dep.replace(".git", "").rstrip("/")
                    if "github.com" not in clean_url:
                        clean_url = f"https://github.com/{author}/{lib_name}"
                    url = f"{clean_url}/archive/refs/heads/{branch}.zip"
                    root = download_and_extract_zip(url, target_dir)
                    break
                except Exception as e:
                    print(f"{indent}   ⚠️ Branch {branch} failed: {e}")
                    continue
            if root is None:
                raise RuntimeError(f"Failed downloading: {dep}")
        else:
            # PlatformIO library
            try:
                pio_url = f"https://api.registry.platformio.org/v3/lib/download/{author}/{lib_name}"
                if version:
                    pio_url += f"?version={version}"
                root = download_and_extract_zip(pio_url, target_dir)
            except Exception as e:
                print(f"{indent}   ⚠️ PlatformIO failed ({e}), using GitHub...")
                for branch in ["main", "master"]:
                    try:
                        url = f"https://github.com/{author}/{lib_name}/archive/refs/heads/{branch}.zip"
                        root = download_and_extract_zip(url, target_dir)
                        break
                    except Exception as e2:
                        print(f"{indent}   ⚠️ GitHub branch {branch} failed: {e2}")
                        continue
                if root is None:
                    raise RuntimeError(f"Download failed for {dep}")

        # -------- CHECK FOR NESTED DEPENDENCIES --------
        nested_deps = []

        # Check for PlatformIO library.json
        lib_json = root / "library.json"
        if lib_json.exists():
            try:
                with open(lib_json, "r", encoding="utf-8") as f:
                    data = json.load(f)

                # Extract dependencies from library.json
                if "dependencies" in data:
                    for dep_info in data["dependencies"]:
                        if isinstance(dep_info, dict):
                            dep_name = dep_info.get("name", "")
                            dep_version = dep_info.get("version", "")
                            # Convert to our format: author/library
                            # PlatformIO sometimes uses just library name, sometimes author/library
                            if "/" in dep_name:
                                nested_deps.append(
                                    dep_name
                                    + (f"@{dep_version}" if dep_version else "")
                                )
                            else:
                                # Try to guess author - for common Arduino libs
                                nested_deps.append(
                                    f"bblanchon/{dep_name}"
                                    + (f"@{dep_version}" if dep_version else "")
                                )
            except Exception as e:
                print(f"{indent}   ⚠️ Failed to parse library.json: {e}")

        # Check for Arduino library.properties
        lib_props = root / "library.properties"
        if lib_props.exists():
            try:
                with open(lib_props, "r", encoding="utf-8") as f:
                    content = f.read()
                    # Parse depends line
                    for line in content.split("\n"):
                        if line.startswith("depends="):
                            deps_str = line.split("=", 1)[1].strip()
                            if deps_str:
                                for dep_name in deps_str.split(","):
                                    dep_name = dep_name.strip()
                                    if dep_name:
                                        # Arduino libraries usually don't have authors in depends
                                        nested_deps.append(f"bblanchon/{dep_name}")
            except Exception as e:
                print(f"{indent}   ⚠️ Failed to parse library.properties: {e}")

        # -------- HANDLE CMAKELISTS.TXT --------
        cmake_file = root / "CMakeLists.txt"

        if cmake_file.exists():
            print(f"{indent}   📄 Using library's existing CMakeLists.txt")

            # Add COMPONENT_NAME if missing
            content = cmake_file.read_text()
            if "idf_component_register" in content and "COMPONENT_NAME" not in content:
                new_content = re.sub(
                    r"(idf_component_register\s*\()",
                    r"\1\n    COMPONENT_NAME " + lib_name,
                    content,
                )
                cmake_file.write_text(new_content)
                print(f"{indent}   🔧 Added COMPONENT_NAME {lib_name}")
        else:
            print(f"{indent}   📄 Generating minimal CMakeLists.txt")

            # Collect source files
            sources = []
            include_dirs = set()

            # Look for source files
            for pattern in [
                "src/*.cpp",
                "src/*.c",
                "*.cpp",
                "*.c",
                "src/**/*.cpp",
                "src/**/*.c",
            ]:
                for f in root.glob(pattern):
                    if (
                        f.is_file()
                        and "test" not in str(f).lower()
                        and "example" not in str(f).lower()
                    ):
                        rel_path = f.relative_to(root)
                        sources.append(str(rel_path).replace("\\", "/"))

            # Find include directories
            for pattern in ["**/*.h", "**/*.hpp"]:
                for f in root.glob(pattern):
                    if f.is_file():
                        rel_dir = f.parent.relative_to(root)
                        if str(rel_dir) != ".":
                            include_dirs.add(str(rel_dir).replace("\\", "/"))

            # Add common include dirs
            if (root / "src").exists():
                include_dirs.add("src")
            if (root / "include").exists():
                include_dirs.add("include")

            include_dirs_str = " ".join(f'"{d}"' for d in sorted(include_dirs)) or "."

            # Generate CMakeLists.txt
            cmake_content = f"""idf_component_register(
    COMPONENT_NAME {lib_name}
"""

            if sources:
                cmake_content += f'    SRCS {" ".join(f"{s}" for s in sources[:50])}\n'

            cmake_content += f"    INCLUDE_DIRS {include_dirs_str}\n"

            # Add arduino requirement for Arduino libraries
            is_arduino_lib = (
                (root / "library.properties").exists()
                or (root / "library.json").exists()
                or "arduino" in lib_name.lower()
            )

            if is_arduino_lib:
                cmake_content += "    REQUIRES arduino\n"

            cmake_content += ")"
            cmake_file.write_text(cmake_content)

        print(f"{indent}   ✔ Installed: {lib_name}")

        # -------- RECURSIVELY INSTALL NESTED DEPENDENCIES --------
        if nested_deps:
            print(f"{indent}   🔍 Found {len(nested_deps)} nested dependencies:")
            for nested_dep in nested_deps:
                print(f"{indent}     - {nested_dep}")

            # Recursive call
            install_dependencies(
                nested_deps,
                build_dir,
                already_installed=already_installed,
                depth=depth + 1,
            )

    if depth == 0:
        print(f"\n✅ All dependencies installed successfully!")
        print(f"📁 Location: {components_auto.relative_to(build_dir)}")


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

    build_path = Path(f"{app_dir}/espidf_projects/{project_id}")

    create_espidf_project(app_dir, project_id)
    merge_arduino_includes_into_idf(build_path, ARDUINO_TEMPLATE)
    convert_arduino_libs_to_idf_components(build_path, ARDUINO_TEMPLATE)

    dependencies = transpiler_metadata["dependencies"]
    dependencies.append("bblanchon/ArduinoJson")
    dependencies.append("adafruit/Adafruit_BusIO")
    install_dependencies(dependencies, build_path)

    # --------------------------------------------------------------------
    # TODO: Insert your future ESP-IDF custom build system here.
    #       Examples: calling idf.py, or direct Ninja build, or esptool.
    # --------------------------------------------------------------------

    # Placeholder message for later extension
    await session.send(
        SessionPhase.BEGIN_COMPILE, "ESP-IDF custom pipeline placeholder executing..."
    )

    # Pretend build/upload succeeded
    upload_success = upload_requested  # simply echo for now

    # Finish
    await session.send(SessionPhase.ALL_DONE, "ESP-IDF custom pipeline finished")

    return {
        "success": True,
        "upload_success": upload_success,
        "session_id": session.id,
        "build_dir": str(build_dir),
    }
