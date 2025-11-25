# ======================================================================
#   ENHANCED MOJOSCALE COMPILE BACKEND
#   Ultra-short paths, smart caching, ESP-DL workarounds, fast builds
# ======================================================================

import shutil
import os
import subprocess
import asyncio
import sys
import uuid
import sqlite3
import serial.tools.list_ports
import webview
import time
import textwrap
import hashlib
import fnmatch
import requests
import zipfile
from pathlib import Path
from enum import Enum
from typing import Optional, Dict, Any, List

from core.utils import get_bundled_python_exe
from core.db import db_path as DB_PATH
from core.transpiler.transpiler import main as transpiler_main
from core.utils import get_app_dir


# ============================================================================
# CONFIG — BUILD FLAGS
# ============================================================================
CORE_BUILD_FLAGS = [
    "-std=gnu++17",
    "-DCONFIG_ARDUINO_IS_ESP_IDF=1",
    "-DARDUINO_USB_MODE=1",
    "-DSPIFFS_USE_LEGACY=1",
]

ESPIDF_BUILD_FLAGS = [
    "-DCONFIG_SCCB_CLK_FREQ=100000",
    "-DCONFIG_XCLK_FREQ=20000000",
    "-DCONFIG_SOC_RESERVED_MEMORY_REGION_SIZE=0x100000",
    # "-DCONFIG_ESP32_DPORT_WORKAROUND=y",
    "-Wno-error",
    "-DCONFIG_OV7670_SUPPORT=1",
    "-DCONFIG_OV7725_SUPPORT=1",
    "-DCONFIG_SCCB_HARDWARE_I2C=1",
    "-DCONFIG_SCCB_HARDWARE_I2C_PORT=1",
    "-DCONFIG_ESP_HTTPS_SERVER_ENABLE=0",
    "-DIDF_CMAKE=y",
    "-DCMAKE_BUILD_PARALLEL_LEVEL=4",
    "-fexceptions",
    "-DARDUINO=1",
    "-DCONFIG_ARDUINO_SELECTIVE_COMPILATION=1",
    "-DCONFIG_ARDUINO_SELECTIVE_ESP_SR=0",
    "-O1",
]

ESPIDF_EMBED_TXT_FILES = [
    "managed_components/espressif__esp_insights/server_certs/https_server.crt",
    "managed_components/espressif__esp_rainmaker/server_certs/rmaker_mqtt_server.crt",
    "managed_components/espressif__esp_rainmaker/server_certs/rmaker_claim_service_server.crt",
    "managed_components/espressif__esp_rainmaker/server_certs/rmaker_ota_server.crt",
]


STARTER_TEMPLATE_ESPIDF = (
    Path(__file__).resolve().parent.parent
    / "core"
    / "transpiler"
    / "runtime"
    / "starter_template_espidf"
)

STARTER_TEMPLATE_ARDUINO = (
    Path(__file__).resolve().parent.parent
    / "core"
    / "transpiler"
    / "runtime"
    / "starter_template"
)


# ============================================================================
# INTERNAL CMP DIR STRUCTURE
# ============================================================================
def init_cmp_dirs(user_app_dir: str):
    """
    Create and return:
    cmp_root   = <user_app_dir>/.cmp
    pio_home   = <user_app_dir>/.cmp/p
    build_root = <user_app_dir>/.cmp/t
    temp_root  = <user_app_dir>/.cmp/x
    """

    CMP_ROOT = Path(user_app_dir) / ".cmp"
    CMP_ROOT.mkdir(parents=True, exist_ok=True)

    PIO_HOME = CMP_ROOT / "p"
    BUILD_ROOT = CMP_ROOT / "t"
    TEMP_ROOT = CMP_ROOT / "x"

    PIO_HOME.mkdir(parents=True, exist_ok=True)
    BUILD_ROOT.mkdir(parents=True, exist_ok=True)
    TEMP_ROOT.mkdir(parents=True, exist_ok=True)

    return CMP_ROOT, PIO_HOME, BUILD_ROOT, TEMP_ROOT


# ============================================================================
# PLATFORMIO INSTALLER / BOOTSTRAP
# ============================================================================
def ensure_platformio_installed(PIO_HOME: Path):
    """
    Ensures PlatformIO Core is installed in:
        <user_app_dir>/.cmp/p/

    Using virtualenv:
        <user_app_dir>/.cmp/p/v/
    """
    VENV = PIO_HOME / "v"

    # Determine python.exe of the venv
    if sys.platform == "win32":
        python_exe = VENV / "Scripts" / "python.exe"
    else:
        python_exe = VENV / "bin" / "python"

    # If missing → create venv and install PlatformIO
    if not python_exe.exists():
        print("🚀 Creating PlatformIO virtual environment...")

        # Use system python to create the venv
        subprocess.run([sys.executable, "-m", "venv", str(VENV)], check=True)

        print("🚀 Upgrading pip...")
        subprocess.run(
            [str(python_exe), "-m", "pip", "install", "--upgrade", "pip"], check=True
        )

        print("🚀 Installing PlatformIO Core...")
        subprocess.run(
            [str(python_exe), "-m", "pip", "install", "platformio"], check=True
        )

        print("✔ PlatformIO installed successfully.")

    return python_exe


# ============================================================================
# WINDOWS: Hide subprocess windows
# ============================================================================
if os.name == "nt":
    _orig_popen = subprocess.Popen

    def _quiet_popen(*args, **kwargs):
        kwargs.setdefault("creationflags", 0)
        kwargs["creationflags"] |= subprocess.CREATE_NO_WINDOW
        si = kwargs.get("startupinfo") or subprocess.STARTUPINFO()
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        kwargs["startupinfo"] = si
        return _orig_popen(*args, **kwargs)

    subprocess.Popen = _quiet_popen


# ============================================================================
# SESSION SYSTEM
# ============================================================================
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


class CompilerEvent:
    def __init__(self, phase: SessionPhase, text: str, level: str = "info"):
        self.phase = phase
        self.text = text
        self.level = level
        self.timestamp = time.time()

    def to_dict(self):
        return {
            "phase": self.phase.value,
            "text": self.text,
            "level": self.level,
            "timestamp": self.timestamp,
        }


class CompilerSession:
    def __init__(self, session_id: str = None):
        self.id = session_id or str(uuid.uuid4())
        self.process: Optional[asyncio.subprocess.Process] = None
        self.cancelled = False

    async def send(self, phase: SessionPhase, text: str, level: str = "info"):
        event = CompilerEvent(phase, text, level)
        print(f"[{phase.value}] {text}")

        try:
            webview.windows[0].evaluate_js(
                f"window.__onCompilerEvent({event.to_dict()})"
            )
        except:
            pass

    async def cancel(self):
        if self.cancelled:
            return
        self.cancelled = True

        if self.process and self.process.returncode is None:
            try:
                self.process.terminate()
                await asyncio.sleep(0.5)
                if self.process.returncode is None:
                    self.process.kill()
            except ProcessLookupError:
                pass

        await self.send(SessionPhase.CANCELLED, "Build cancelled by user", "warn")


_active_sessions: Dict[str, CompilerSession] = {}


def create_session() -> CompilerSession:
    s = CompilerSession()
    _active_sessions[s.id] = s
    return s


def cancel_session(session_id: str):
    sess = _active_sessions.get(session_id)
    if sess:
        asyncio.create_task(sess.cancel())
        return True
    return False


# ============================================================================
# SMART ESP-DL COMPONENT MANAGEMENT
# ============================================================================
def find_esp_sr_dependency_source(build_dir: Path):
    """
    Find which component is declaring ESP-SR as a dependency
    """
    print("🔍 Searching for ESP-SR dependency sources...")

    # Check all idf_component.yml files
    for root in [
        build_dir / "components",
        build_dir / "managed_components",
        build_dir / "components_auto",
    ]:
        if not root.exists():
            continue

        for yml_file in root.rglob("idf_component.yml"):
            try:
                content = yml_file.read_text()
                if "esp-sr" in content or "esp_sr" in content:
                    print(f"🚨 FOUND: {yml_file} declares ESP-SR dependency")
                    print(f"   Content snippet: {content[:200]}...")
            except:
                pass

    # Check CMakeLists.txt files for dependencies
    for root in [
        build_dir / "components",
        build_dir / "managed_components",
        build_dir / "components_auto",
    ]:
        if not root.exists():
            continue

        for cmake_file in root.rglob("CMakeLists.txt"):
            try:
                content = cmake_file.read_text()
                if "esp-sr" in content or "esp_sr" in content:
                    print(f"🚨 FOUND: {cmake_file} references ESP-SR")
                    print(f"   Content snippet: {content[:200]}...")
            except:
                pass

    # Check dependencies.lock if it exists
    lock_file = build_dir / "dependencies.lock"
    if lock_file.exists():
        try:
            content = lock_file.read_text()
            if "esp-sr" in content or "esp_sr" in content:
                print("🚨 FOUND: dependencies.lock contains ESP-SR")
                # Extract the relevant section
                lines = content.split("\n")
                for i, line in enumerate(lines):
                    if "esp-sr" in line or "esp_sr" in line:
                        start = max(0, i - 2)
                        end = min(len(lines), i + 3)
                        print("   Context:")
                        for j in range(start, end):
                            print(f"   {lines[j]}")
        except:
            pass


def remove_sr_components(build_dir: Path):
    """
    Remove ALL speech-recognition components with better pattern matching
    """
    sr_patterns = [
        # Registry names (with hyphens)
        "espressif__esp-sr",
        "espressif__esp-voice",
        "espressif__esp-sr-front-end",
        # Local names (with hyphens)
        "esp-sr",
        "esp-voice",
        "esp-sr-front-end",
        # Underscore variants (common in CMake)
        "espressif__esp_sr",
        "espressif__esp_voice",
        "espressif__esp_sr_front_end",
        "esp_sr",
        "esp_voice",
        "esp_sr_front_end",
        # Any component containing "sr" or "voice"
        "*sr*",
        "*voice*",
    ]

    managed = build_dir / "managed_components"
    comp = build_dir / "components"
    comp_auto = build_dir / "components_auto"

    removed = False

    # First, debug what we find
    print("🔍 Scanning for SR components...")
    for root in [managed, comp, comp_auto]:
        if not root.exists():
            continue
        for item in root.iterdir():
            if item.is_dir():
                for pattern in sr_patterns:
                    # Exact match
                    if pattern == item.name:
                        print(f"🎯 Found SR component: {item}")
                        break
                    # Wildcard match
                    elif "*" in pattern and fnmatch.fnmatch(item.name, pattern):
                        print(
                            f"🎯 Found SR component (wildcard): {item} matches {pattern}"
                        )
                        break

    # Now remove them
    for root in [managed, comp, comp_auto]:
        if not root.exists():
            continue
        for pattern in sr_patterns:
            if "*" in pattern:
                # Handle wildcard patterns
                for item in root.glob(pattern):
                    if item.exists():
                        print(f"🧹 Removing SR component (wildcard): {item}")
                        shutil.rmtree(item, ignore_errors=True)
                        removed = True
            else:
                # Handle exact matches
                target = root / pattern
                if target.exists():
                    print(f"🧹 Removing SR component: {target}")
                    shutil.rmtree(target, ignore_errors=True)
                    removed = True

    if removed:
        print("✅ SR components removed")
    else:
        print("ℹ No SR components found")

    # Also remove dependencies.lock to force re-resolution
    lock_file = build_dir / "dependencies.lock"
    if lock_file.exists():
        print("🧹 Removing dependencies.lock to force re-resolution")
        lock_file.unlink(missing_ok=True)


def ensure_espdl_installed_smart(build_dir: Path, user_app_dir: str) -> bool:
    """
    Smart ESP-DL installation that ensures include paths are properly set up
    """
    managed_dir = build_dir / "managed_components"
    espdl_dir = managed_dir / "espressif__esp-dl"

    # Check if already properly installed with correct structure
    if espdl_dir.exists() and (espdl_dir / "include" / "dl").exists():
        print("✅ ESP-DL already installed and valid")
        return True

    # Create persistent cache for ESP-DL
    cache_root = Path(user_app_dir) / ".component_cache"
    cache_root.mkdir(parents=True, exist_ok=True)

    espdl_cache = cache_root / "esp-dl"

    try:
        # Method 1: Direct Git clone (bypasses idf.py)
        if not espdl_cache.exists():
            print("⬇️ Downloading ESP-DL via direct Git clone...")
            result = subprocess.run(
                [
                    "git",
                    "clone",
                    "--depth",
                    "1",
                    "https://github.com/espressif/esp-dl.git",
                    str(espdl_cache),
                ],
                check=False,
                capture_output=True,
                text=True,
                timeout=120,
            )

            if result.returncode != 0:
                print(f"⚠️ Git clone failed: {result.stderr}")
                raise Exception("Git clone failed")

        # Copy to managed components
        managed_dir.mkdir(parents=True, exist_ok=True)
        if espdl_dir.exists():
            shutil.rmtree(espdl_dir)

        # Copy the entire ESP-DL structure - it has components/esp-dl/ inside
        if (espdl_cache / "components" / "esp-dl").exists():
            # New structure: components/esp-dl/
            shutil.copytree(espdl_cache / "components" / "esp-dl", espdl_dir)
            print("✅ ESP-DL installed (new structure: components/esp-dl/)")
        elif (espdl_cache / "esp-dl").exists():
            # Alternative structure: esp-dl/ at root
            shutil.copytree(espdl_cache / "esp-dl", espdl_dir)
            print("✅ ESP-DL installed (root esp-dl/ structure)")
        else:
            # Fallback: copy entire repo
            shutil.copytree(espdl_cache, espdl_dir)
            print("✅ ESP-DL installed (full repo structure)")

        # Verify the structure has the required headers
        model_header = espdl_dir / "include" / "dl" / "model" / "model.hpp"
        if not model_header.exists():
            print("⚠️ ESP-DL missing required headers, creating stubs...")
            create_espdl_stub_headers(espdl_dir)

        return True

    except Exception as e:
        print(f"⚠️ Direct Git method failed: {e}")

        # Method 2: Use component registry API
        try:
            return install_espdl_via_registry(build_dir)
        except Exception as e2:
            print(f"❌ Registry method failed: {e2}")

            # Method 3: Create proper component structure
            try:
                return create_proper_espdl_component(build_dir)
            except Exception as e3:
                print(f"❌ All ESP-DL installation methods failed: {e3}")
                return False


def install_espdl_via_registry(build_dir: Path) -> bool:
    """
    Alternative: Download component via GitHub API
    """
    managed_dir = build_dir / "managed_components"
    managed_dir.mkdir(parents=True, exist_ok=True)

    # Download latest release
    url = "https://github.com/espressif/esp-dl/archive/refs/heads/master.zip"

    try:
        print("⬇️ Downloading ESP-DL via direct download...")
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()

        zip_path = build_dir / "esp-dl-temp.zip"
        with open(zip_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

        # Extract
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(managed_dir)

        # Rename to expected format
        extracted = managed_dir / "esp-dl-master"
        target = managed_dir / "espressif__esp-dl"

        if extracted.exists():
            if target.exists():
                shutil.rmtree(target)
            extracted.rename(target)

        zip_path.unlink(missing_ok=True)

        # Verify structure and create stubs if needed
        espdl_dir = managed_dir / "espressif__esp-dl"
        model_header = espdl_dir / "include" / "dl" / "model" / "model.hpp"
        if not model_header.exists():
            print("⚠️ Downloaded ESP-DL missing headers, creating stubs...")
            create_espdl_stub_headers(espdl_dir)

        print("✅ ESP-DL installed via direct download")
        return True

    except Exception as e:
        print(f"❌ Registry download failed: {e}")
        return False


def create_proper_espdl_component(build_dir: Path) -> bool:
    """
    Create a properly structured ESP-DL component with correct CMake configuration
    """
    managed_dir = build_dir / "managed_components"
    espdl_dir = managed_dir / "espressif__esp-dl"

    managed_dir.mkdir(parents=True, exist_ok=True)

    if espdl_dir.exists():
        shutil.rmtree(espdl_dir)

    espdl_dir.mkdir(parents=True, exist_ok=True)

    # Create proper CMakeLists.txt that includes all necessary paths
    cmake_content = """\
idf_component_register(
    SRCS ""
    INCLUDE_DIRS 
        "include"
        "include/dl"
        "include/dl/layer"
        "include/dl/layer/private"
        "include/dl/op"
        "include/dl/op/private" 
        "include/dl/model"
        "include/dl/vision"
        "include/dl/vision/private"
        "include/dl/tool"
    REQUIRES 
        freertos 
        nvs_flash 
        esp_timer
        heap
        log
        soc
        hal
        esp_common
        esp_rom
        esp_system
)
"""
    (espdl_dir / "CMakeLists.txt").write_text(cmake_content)

    # Create directory structure and stub headers
    create_espdl_stub_headers(espdl_dir)

    print("⚠️ Created ESP-DL stub component (limited functionality)")
    return True


def create_espdl_stub_headers(espdl_dir: Path):
    """
    Create minimal stub headers to satisfy common ESP-DL includes
    """
    # Create directory structure
    include_dirs = [
        "include/dl",
        "include/dl/layer",
        "include/dl/layer/private",
        "include/dl/op",
        "include/dl/op/private",
        "include/dl/model",
        "include/dl/vision",
        "include/dl/vision/private",
        "include/dl/tool",
    ]

    for dir_path in include_dirs:
        (espdl_dir / dir_path).mkdir(parents=True, exist_ok=True)

    # Create main dl header
    (espdl_dir / "include" / "dl" / "dl.hpp").write_text(
        """\
#pragma once
#define DL_MINIMAL_STUB 1
namespace dl {
    // Stub implementation
}
"""
    )

    # Create model header that's being requested
    (espdl_dir / "include" / "dl" / "model" / "model.hpp").write_text(
        """\
#pragma once
#include "../dl.hpp"
namespace dl {
namespace model {
    // Stub model implementation
    class Model {
    public:
        virtual ~Model() = default;
    };
}
}
"""
    )

    # Create common layer headers
    (espdl_dir / "include" / "dl" / "layer" / "layer.hpp").write_text(
        """\
#pragma once
#include "../dl.hpp"
namespace dl {
namespace layer {
    // Stub layer implementation
}
}
"""
    )

    # Create additional stub headers that might be needed
    (espdl_dir / "include" / "dl" / "op" / "op.hpp").write_text(
        """\
#pragma once
#include "../dl.hpp"
namespace dl {
namespace op {
    // Stub op implementation
}
}
"""
    )

    print("✅ Created ESP-DL stub headers")


def add_espdl_to_build_flags(build_flags: List[str], build_dir: Path) -> List[str]:
    """
    Add ESP-DL specific include paths to build flags
    """
    espdl_dir = build_dir / "managed_components" / "espressif__esp-dl"

    if espdl_dir.exists():
        # Add main include path
        build_flags.append(f'-I{espdl_dir / "include"}')

        # Add specific subdirectories that might be needed
        sub_dirs = ["dl", "dl/layer", "dl/model", "dl/op", "dl/vision", "dl/tool"]

        for sub_dir in sub_dirs:
            include_path = espdl_dir / "include" / sub_dir
            if include_path.exists():
                build_flags.append(f"-I{include_path}")

    return build_flags


# ============================================================================
# PERSISTENT BUILD CACHE SYSTEM
# ============================================================================
def setup_persistent_cache(build_dir: Path, user_app_dir: str) -> Dict[str, str]:
    """
    Set up persistent build cache to avoid recompilation
    """
    cache_root = Path(user_app_dir) / ".build_cache"
    cache_root.mkdir(parents=True, exist_ok=True)

    cache_dirs = {
        "build": cache_root / "build",
        ".pio": cache_root / "pio",
        "managed_components": cache_root / "managed_components",
    }

    env_vars = {}

    for name, cache_path in cache_dirs.items():
        cache_path.mkdir(exist_ok=True)

        # Link build directory to cache
        build_subdir = build_dir / name
        if build_subdir.exists():
            if build_subdir.is_symlink():
                build_subdir.unlink()
            else:
                shutil.rmtree(build_subdir)

        # Create symlink/junction to cache
        try:
            if sys.platform == "win32":
                # Windows: use junction points
                import _winapi

                try:
                    _winapi.CreateJunction(str(cache_path), str(build_subdir))
                except:
                    # Fallback to directory copy if junction fails
                    shutil.copytree(cache_path, build_subdir)
            else:
                # Unix: use symlinks
                build_subdir.symlink_to(cache_path)

            print(f"🔗 Linked {name} → persistent cache")

        except Exception as e:
            print(f"⚠️ Cache linking failed for {name}: {e}")
            # Continue without cache for this directory

    return env_vars


def get_component_hash(build_dir: Path) -> str:
    """
    Generate hash of component state to detect changes
    """
    hash_data = []

    # Hash component directories
    component_dirs = [
        build_dir / "components",
        build_dir / "managed_components",
        build_dir / "main",
    ]

    for comp_dir in component_dirs:
        if comp_dir.exists():
            for file_path in comp_dir.rglob("*"):
                if file_path.is_file() and file_path.suffix in [
                    ".c",
                    ".cpp",
                    ".h",
                    ".hpp",
                    ".cmake",
                    "",
                ]:
                    try:
                        stat = file_path.stat()
                        hash_data.append(f"{file_path}:{stat.st_mtime}:{stat.st_size}")
                    except:
                        pass

    # Hash platformio.ini and CMakeLists.txt files
    config_files = [
        build_dir / "platformio.ini",
        build_dir / "sdkconfig.defaults",
        build_dir / "CMakeLists.txt",
    ]

    for config_file in config_files:
        if config_file.exists():
            hash_data.append(config_file.read_text())

    content = "|".join(hash_data)
    return hashlib.md5(content.encode()).hexdigest()


def should_rebuild(build_dir: Path, cache_dir: Path) -> bool:
    """
    Check if rebuild is necessary based on component changes
    """
    current_hash = get_component_hash(build_dir)
    hash_file = cache_dir / "build_hash.txt"

    if hash_file.exists():
        previous_hash = hash_file.read_text().strip()
        if previous_hash == current_hash:
            print("🔁 No changes detected, using cached build")
            return False

    # Update hash for next build
    hash_file.parent.mkdir(parents=True, exist_ok=True)
    hash_file.write_text(current_hash)
    print("🔁 Changes detected, rebuilding...")
    return True


# ============================================================================
# BUILD FOLDER HANDLING
# ============================================================================
def find_real_pio_package_dir() -> Path:
    """
    Locate the real PIO global packages dir regardless of venv location.
    """
    # 1. PIO_HOME environment variable (if set)
    if "PLATFORMIO_CORE_DIR" in os.environ:
        p = Path(os.environ["PLATFORMIO_CORE_DIR"]) / "packages"
        if p.exists():
            return p

    # 2. Default user-level PIO install path
    # Windows
    win = Path.home() / ".platformio" / "packages"
    if win.exists():
        return win

    # Unix/Linux/macOS
    unix = Path(os.path.expanduser("~/.platformio/packages"))
    if unix.exists():
        return unix

    raise RuntimeError("Cannot locate global PlatformIO package directory")


def get_arduino_cache_dir(user_app_dir: Path) -> Path:
    """Get the persistent Arduino component cache directory"""
    return user_app_dir / ".arduino_component_cache"


def clone_arduino_component(component_dir: Path, user_app_dir: str):
    """
    Clone Arduino-ESP32 into components/arduino from cache if available
    """
    arduino_dir = component_dir / "arduino"

    if arduino_dir.exists():
        print("🔁 Arduino component already exists in build, skipping.")
        return

    # Get cache directory
    cache_dir = get_arduino_cache_dir(Path(user_app_dir))
    cache_dir.mkdir(parents=True, exist_ok=True)

    arduino_cache = cache_dir / "arduino-esp32"

    # Check if cache exists and is valid
    if arduino_cache.exists() and (arduino_cache / ".git").exists():
        print("📦 Using cached Arduino component...")
        try:
            # Verify it's the right version
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=str(arduino_cache),
                capture_output=True,
                text=True,
                check=True,
            )
            print(f"🔍 Cache commit: {result.stdout.strip()[:8]}")

            # Copy from cache to build directory
            shutil.copytree(arduino_cache, arduino_dir, symlinks=False)
            print("✅ Arduino component copied from cache")
            return

        except (subprocess.CalledProcessError, Exception) as e:
            print(f"⚠️  Cache corrupted, re-downloading: {e}")
            shutil.rmtree(arduino_cache, ignore_errors=True)

    # Download fresh if cache doesn't exist or is corrupted
    print("⬇️  Downloading Arduino-ESP32 v3.3.4 as ESP-IDF component...")

    try:
        subprocess.run(
            [
                "git",
                "clone",
                "--recursive",
                "https://github.com/espressif/arduino-esp32.git",
                str(arduino_cache),
            ],
            check=True,
        )

        # Checkout specific version
        subprocess.run(["git", "checkout", "3.3.4"], cwd=str(arduino_cache), check=True)

        subprocess.run(
            ["git", "submodule", "update", "--init", "--recursive"],
            cwd=str(arduino_cache),
            check=True,
        )

        # Now copy from cache to build
        shutil.copytree(arduino_cache, arduino_dir, symlinks=False)
        print(f"✅ Arduino ESP32 component installed and cached at: {arduino_cache}")

    except Exception as e:
        print(f"❌ Failed to clone Arduino component: {e}")
        # Clean up failed cache
        shutil.rmtree(arduino_cache, ignore_errors=True)
        raise


def merge_arduino_includes_into_idf(build_dir: Path, STARTER_TEMPLATE_ARDUINO: Path):
    """
    Copies all .h / .hpp files from the Arduino starter template 'include'
    into the ESP-IDF component: components/mojoscale_arduino/include/
    """

    src_include = STARTER_TEMPLATE_ARDUINO / "include"
    dst_include = build_dir / "components" / "mojoscale_arduino" / "include"

    if not src_include.exists():
        print(f"⚠️ No Arduino include/ folder found at {src_include}")
        return

    dst_include.mkdir(parents=True, exist_ok=True)

    print("📥 Copying Arduino template headers → ESP-IDF component include/")
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
    Converts all folders inside Arduino template 'lib/' into ESP-IDF components
    under build_dir/components_auto/<libname>/
    """

    libs_dir = STARTER_TEMPLATE_ARDUINO / "lib"
    components_auto = build_dir / "components_auto"
    components_auto.mkdir(exist_ok=True)

    if not libs_dir.exists():
        print(f"⚠️ No Arduino lib/ folder found at {libs_dir}")
        return

    print("📦 Converting Arduino lib/ → ESP-IDF components_auto/")

    for lib in libs_dir.iterdir():
        if not lib.is_dir():
            continue

        comp = components_auto / lib.name
        comp.mkdir(parents=True, exist_ok=True)

        # Copy entire library folder structure
        shutil.copytree(lib, comp, dirs_exist_ok=True)

        # Collect sources
        sources = []
        includes = set()

        for src in comp.rglob("*.c"):
            sources.append(str(src.relative_to(comp)).replace("\\", "/"))
        for src in comp.rglob("*.cpp"):
            sources.append(str(src.relative_to(comp)).replace("\\", "/"))
        for h in comp.rglob("*.h"):
            includes.add(str(h.parent.relative_to(comp)))
        for h in comp.rglob("*.hpp"):
            includes.add(str(h.parent.relative_to(comp)))

        include_dirs = " ".join(f'"{x}"' for x in includes if x != ".")

        # Write CMakeLists.txt
        cmk = comp / "CMakeLists.txt"
        cmk.write_text(
            f"""
idf_component_register(
    SRCS {" ".join(f'"{s}"' for s in sources)}
    INCLUDE_DIRS {include_dirs if include_dirs else "."}
)
"""
        )
        print(f"   ✔ Created component: {comp}")


def prepare_build_folder(framework, BUILD_ROOT: Path, STARTER_TEMPLATE: Path) -> Path:
    """
    Prepare a build folder and inject Arduino-as-component when framework == espidf
    """

    user_app_dir = get_app_dir()

    build_id = str(uuid.uuid4())[:6]
    build_dir = BUILD_ROOT / build_id

    shutil.copytree(STARTER_TEMPLATE, build_dir, dirs_exist_ok=True)
    print(f"📁 Build folder prepared at {build_dir}")

    # ===========================================
    # ESP-IDF MODE → INSTALL ARDUINO COMPONENT
    # ===========================================
    if framework == "espidf":
        components_dir = build_dir / "components"
        components_dir.mkdir(parents=True, exist_ok=True)

        # Clone Arduino-as-component (with caching)
        try:
            clone_arduino_component(components_dir, user_app_dir)
        except Exception as e:
            print(f"❌ Failed to clone Arduino component: {e}")
            raise

        # ESP-IDF expects CMakeLists.txt in main/, so move transpilations there
        main_dir = build_dir / "main"
        main_dir.mkdir(exist_ok=True)

        # ---------------------------------------------
        # Inject Arduino template → ESP-IDF environment
        # ---------------------------------------------
        merge_arduino_includes_into_idf(build_dir, STARTER_TEMPLATE_ARDUINO)
        convert_arduino_libs_to_idf_components(build_dir, STARTER_TEMPLATE_ARDUINO)

        print("✔ Arduino template integrated into ESP-IDF environment")

    else:
        src_dir = build_dir / "src"
        src_dir.mkdir(parents=True, exist_ok=True)

    return build_dir


def cleanup_build_folder(build_dir: Path):
    try:
        shutil.rmtree(build_dir, ignore_errors=True)
        print(f"🧹 Cleaned build folder {build_dir}")
    except:
        pass


# ============================================================================
# WRITE TRANSPILER OUTPUT
# ============================================================================
def write_transpiled_code(files: dict, build_dir: Path, framework: str):
    if framework == "espidf":
        src_dir = build_dir / "src"
        include_dir = build_dir / "components" / "mojoscale_arduino" / "include"
    else:
        src_dir = build_dir / "src"
        include_dir = build_dir / "include"

    src_dir.mkdir(parents=True, exist_ok=True)
    include_dir.mkdir(parents=True, exist_ok=True)

    for name, code in files.items():
        if name == "main.py":
            out = src_dir / "main.cpp"
        else:
            out = include_dir / name.replace(".py", ".h")
        out.write_text(code, encoding="utf-8")
        print(f"✍️ Wrote {out}")


# ============================================================================
# OPTIMIZED PLATFORMIO CONFIGURATION
# ============================================================================
def write_optimized_platformio_ini(
    board: str,
    platform: str,
    build_dir: Path,
    dependencies: list,
    framework: str,
    embed_files: list,
    TEMP_ROOT: Path,
    use_cache: bool = True,
):
    """Write platformio.ini using ONLY append(), one line at a time."""

    # --------------------------------------------
    # Dependencies
    # --------------------------------------------
    deps = ["ArduinoJson@6.21.4"] + list(set(dependencies or []))

    # --------------------------------------------
    # Build flags
    # --------------------------------------------
    seen = set()
    build_flags = []
    for f in CORE_BUILD_FLAGS:
        if f not in seen:
            seen.add(f)
            build_flags.append(f)

    if framework == "espidf":
        for f in ESPIDF_BUILD_FLAGS:
            if f not in seen:
                seen.add(f)
                build_flags.append(f)

    unflags = [
        "-std=gnu++11",
        "-std=gnu++14",
    ]

    # --------------------------------------------
    # Cache block
    # --------------------------------------------
    cache_block = []
    if use_cache and framework == "espidf":
        cache_block.append("; Build caching")
        cache_block.append("idf_build_cache = true")
        cache_block.append("idf_build_cache_ttl = 86400")
        cache_block.append("idf_build_cache_size = 500M")
        cache_block.append("")
        cache_block.append("; CMake caching")
        cache_block.append("idf_cmake_cache = true")
        cache_block.append("")

    # --------------------------------------------
    # Begin constructing the INI file
    # --------------------------------------------
    ini = []

    ini.append(f"[env:{board}]")
    ini.append(f"platform = {platform}")
    ini.append(f"board = {board}")
    ini.append(f"framework = {framework}")
    ini.append("upload_speed = 921600")
    ini.append("monitor_speed = 115200")
    ini.append("")

    # --------------------------------------------
    # build_unflags
    # --------------------------------------------
    ini.append("build_unflags =")
    for u in unflags:
        ini.append(f"    {u}")
    ini.append("")

    # --------------------------------------------
    # build_flags
    # --------------------------------------------
    ini.append("build_flags =")
    for bf in build_flags:
        ini.append(f"    {bf}")
    ini.append("")

    # --------------------------------------------
    # lib_deps
    # --------------------------------------------
    ini.append("lib_deps =")
    for d in deps:
        ini.append(f"    {d}")
    ini.append("")

    # --------------------------------------------
    # Cache directory
    # --------------------------------------------
    ini.append(f"build_cache_dir = {TEMP_ROOT}")
    ini.append("")

    # --------------------------------------------
    # Cache block (optional)
    # --------------------------------------------
    for line in cache_block:
        ini.append(line)

    # --------------------------------------------
    # ESP-IDF specific
    # --------------------------------------------
    if framework == "espidf":
        ini.append("; ESP-IDF specific")
        ini.append("board_build.sdkconfig = sdkconfig.defaults")
        ini.append("build_src_filter = +<main/> +<components/> +<managed_components/>")
        ini.append("")
        ini.append("board_build.embed_txtfiles = ")

        for text_file in ESPIDF_EMBED_TXT_FILES:
            ini.append(f"    {text_file}")
        ini.append("")

    # --------------------------------------------
    # Parallel builds
    # --------------------------------------------
    ini.append("; Parallel builds")
    ini.append("build_type = release")
    ini.append("jobs = 4")
    ini.append("")

    # --------------------------------------------
    # embed_files
    # --------------------------------------------
    if embed_files:
        ini.append("board_build.embed_files =")
        for f in embed_files:
            ini.append(f"    {f}")
        ini.append("")

    # --------------------------------------------
    # Write to file
    # --------------------------------------------
    final_text = "\n".join(ini)
    (build_dir / "platformio.ini").write_text(final_text, encoding="utf-8")

    print(final_text)
    print("📝 platformio.ini written (append-only clean version)")


def write_sdkconfig_defaults(build_dir: Path):
    sdk = build_dir / "sdkconfig.defaults"
    text = """\
CONFIG_FREERTOS_HZ=1000
CONFIG_NEWLIB_STDOUT_LINE_ENDING_CRLF=y
CONFIG_NEWLIB_STDERR_LINE_ENDING_CRLF=y
CONFIG_BT_ENABLED=n
CONFIG_SCCB_CLK_FREQ=100000
CONFIG_SCCB_HARDWARE_I2C=y
CONFIG_SCCB_HARDWARE_I2C_PORT=1
CONFIG_ARDUINO_SELECTIVE_COMPILATION=y
CONFIG_ARDUINO_SELECTIVE_ESP_SR=n

"""
    sdk.write_text(text, encoding="utf-8")
    print(f"📝 sdkconfig.defaults written at {sdk}")


# ============================================================================
# GET PLATFORMIO COMMAND
# ============================================================================
def get_platformio_command(PIO_HOME: Path):
    python_exe = ensure_platformio_installed(PIO_HOME)

    env = {
        "PLATFORMIO_HOME": str(PIO_HOME),
        "PIO_HOME_DIR": str(PIO_HOME),
        "PLATFORMIO_CORE_DIR": str(PIO_HOME),
    }

    cmd = [
        str(python_exe),
        "-c",
        "import platformio.__main__; platformio.__main__.main()",
    ]

    return cmd, env


# ============================================================================
# UPLOAD PORT DETECTION
# ============================================================================
def find_esp_serial_port() -> Optional[str]:
    ports = list(serial.tools.list_ports.comports())
    for p in ports:
        desc = (p.description or "").lower()
        if any(x in desc for x in ["esp", "ch340", "cp210"]):
            return p.device
    return ports[0].device if ports else None


# ============================================================================
# PARSE RESULT
# ============================================================================
def parse_platformio_result(stdout: str, stderr: str):
    combined = stdout + "\n" + stderr
    failed = any("error:" in line.lower() for line in combined.splitlines())
    return {
        "success": not failed,
        "message": "Build success" if not failed else "Build failed",
        "specs": {},
    }


# ============================================================================
# ENHANCED MAIN COMPILE ROUTINE
# ============================================================================
async def compile_project(
    py_files: dict,
    board: str,
    platform: str,
    user_app_dir: str,
    upload: bool = False,
    port=None,
    dependencies=None,
    use_cache: bool = True,
):
    # INIT PATH STRUCTURE
    CMP_ROOT, PIO_HOME, BUILD_ROOT, TEMP_ROOT = init_cmp_dirs(user_app_dir)

    session = create_session()

    try:
        # -----------------------------------------------------------
        # 1. TRANSPILATION
        # -----------------------------------------------------------
        await session.send(SessionPhase.BEGIN_TRANSPILE, "Transpiling Python code...")

        commit_hash = str(uuid.uuid4()).replace("-", "_")
        DB_CONN = sqlite3.connect(DB_PATH)

        transpiler = transpiler_main(
            commit_hash,
            DB_CONN,
            py_files,
            os.path.join(os.path.dirname(__file__), "transpiler", "core_libs"),
            platform,
        )

        files = transpiler["code"]

        dependencies = (dependencies or []) + transpiler.get("dependencies", [])
        embed_files = transpiler.get("embed_files", [])
        framework = transpiler.get("framework", "arduino")

        await session.send(SessionPhase.END_TRANSPILE, "Transpilation complete")

        # Pretty-print the transpiled C++ code to terminal
        print("\n==================== 🧩 Transpiled Arduino Code ====================\n")
        for name, code in files.items():
            ext = "ino" if name == "main.py" else "h"
            file_label = f"{name.replace('.py', f'.{ext}')}"
            print(f"📄 {file_label}:\n")

            formatted = textwrap.indent(code.strip(), "    ")
            print(formatted)
            print("\n" + "-" * 70 + "\n")

        print("===================== ✅ End of Transpiled Code =====================\n")

        # -----------------------------------------------------------
        # 1A: AUTO UPGRADE PLATFORMIO CORE FOR ESP-IDF BUILDS
        # -----------------------------------------------------------
        if framework == "espidf":
            await session.send(
                SessionPhase.BEGIN_COMPILE, "Upgrading PlatformIO Core to dev branch..."
            )

            upgrade_marker = PIO_HOME / "pio_dev_upgraded.txt"
            python_exe = ensure_platformio_installed(PIO_HOME)

            if not upgrade_marker.exists():
                try:
                    subprocess.run(
                        [
                            str(python_exe),
                            "-m",
                            "pip",
                            "install",
                            "--upgrade",
                            "https://github.com/platformio/platformio-core/archive/develop.zip",
                        ],
                        check=True,
                    )
                    upgrade_marker.write_text("upgraded", encoding="utf-8")
                    await session.send(
                        SessionPhase.BEGIN_COMPILE,
                        "PlatformIO Core upgraded (pip method)",
                    )
                except Exception as e:
                    await session.send(
                        SessionPhase.ERROR, f"PIO upgrade failed via pip: {e}", "error"
                    )
            else:
                await session.send(
                    SessionPhase.BEGIN_COMPILE,
                    "PlatformIO dev already installed, skipping",
                )

        # -----------------------------------------------------------
        # 2. BUILD FOLDER SETUP WITH CACHING
        # -----------------------------------------------------------
        if framework == "espidf":
            STARTER_TEMPLATE = STARTER_TEMPLATE_ESPIDF
        else:
            STARTER_TEMPLATE = STARTER_TEMPLATE_ARDUINO

        await session.send(SessionPhase.BEGIN_COMPILE, "Preparing build folder...")
        build_dir = prepare_build_folder(framework, BUILD_ROOT, STARTER_TEMPLATE)

        # Set up persistent cache
        cache_env = {}
        if use_cache:
            cache_env = setup_persistent_cache(build_dir, user_app_dir)

        # Check if rebuild is needed
        cache_root = Path(user_app_dir) / ".build_cache"
        should_build = True

        if use_cache and cache_root.exists():
            should_build = should_rebuild(build_dir, cache_root)

        if not should_build:
            await session.send(
                SessionPhase.BEGIN_COMPILE, "Using cached build artifacts"
            )
            # We'll skip compilation and go straight to upload if needed
            build_success = True
        else:
            # Install components
            if framework == "espidf":
                find_esp_sr_dependency_source(build_dir)
                # DELETE SR TO PREVENT DEP RESOLUTION
                remove_sr_components(build_dir)
                if not ensure_espdl_installed_smart(build_dir, user_app_dir):
                    await session.send(
                        SessionPhase.ERROR, "ESP-DL installation failed", "error"
                    )
                    return {"success": False, "error": "ESP-DL installation failed"}

                # -----------------------------------------------------------
                # 2A. COPY ESP-DL INTO components/ FOR PLATFORMIO DISCOVERY
                # -----------------------------------------------------------
                try:
                    managed_dir = build_dir / "managed_components" / "espressif__esp-dl"
                    target_dir = build_dir / "components" / "esp-dl"
                    if target_dir.exists():
                        shutil.rmtree(target_dir)
                    shutil.copytree(managed_dir, target_dir)
                    print(f"📦 ESP-DL linked into project components/: {target_dir}")
                except Exception as e:
                    print(f"❌ Failed to copy ESP-DL into components/: {e}")
                    await session.send(
                        SessionPhase.ERROR, "ESP-DL component copy failed", "error"
                    )
                    return {"success": False, "error": "ESP-DL copy failed"}

            write_transpiled_code(files, build_dir, framework)

            if framework == "espidf":
                write_sdkconfig_defaults(build_dir)

            write_optimized_platformio_ini(
                board,
                platform,
                build_dir,
                dependencies,
                framework,
                embed_files,
                TEMP_ROOT,
                use_cache,
            )

            # Copy win_linker_workaround if needed
            try:
                workaround_src = (
                    Path(__file__).resolve().parent / "win_linker_workaround.py"
                )
                workaround_dst = build_dir / "win_linker_workaround.py"

                if workaround_src.exists():
                    shutil.copyfile(workaround_src, workaround_dst)
                    print(f"📝 Copied win_linker_workaround.py → {workaround_dst}")
                else:
                    print(f"⚠️ win_linker_workaround.py not found at {workaround_src}")
            except Exception as copy_err:
                print(f"⚠️ Failed to copy win_linker_workaround.py: {copy_err}")

            # -----------------------------------------------------------
            # 3. RUN PLATFORMIO BUILD
            # -----------------------------------------------------------
            await session.send(SessionPhase.BEGIN_COMPILE, "Starting compilation...")

            pio_cmd, pio_env = get_platformio_command(PIO_HOME)
            env = os.environ.copy()
            env.update(pio_env)
            env.update(cache_env)  # Add cache environment variables
            env["TMP"] = str(TEMP_ROOT)
            env["TEMP"] = str(TEMP_ROOT)

            cmd = pio_cmd + ["run"]

            session.process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(build_dir),
                env=env,
                creationflags=subprocess.CREATE_NO_WINDOW
                if sys.platform == "win32"
                else 0,
            )

            stdout_lines = []
            stderr_lines = []

            async def stream(pipe, collector):
                while True:
                    line = await pipe.readline()
                    if not line:
                        break
                    txt = line.decode(errors="ignore").rstrip()
                    collector.append(txt)
                    await session.send(SessionPhase.BEGIN_COMPILE, txt)

            await asyncio.gather(
                stream(session.process.stdout, stdout_lines),
                stream(session.process.stderr, stderr_lines),
            )

            code = await session.process.wait()
            session.process = None

            parsed = parse_platformio_result(
                "\n".join(stdout_lines), "\n".join(stderr_lines)
            )

            if code != 0 or not parsed["success"]:
                await session.send(SessionPhase.ERROR, "Compilation failed", "error")
                cleanup_build_folder(build_dir)
                return parsed

            build_success = True
            await session.send(SessionPhase.END_COMPILE, "Compilation successful")

        # -----------------------------------------------------------
        # 4. UPLOAD (if build was successful and upload requested)
        # -----------------------------------------------------------
        upload_success = False

        if upload and build_success:
            await session.send(SessionPhase.START_UPLOAD, "Starting upload...")

            actual_port = port or find_esp_serial_port()
            if not actual_port:
                await session.send(SessionPhase.ERROR, "No ESP32 device found", "error")
                cleanup_build_folder(build_dir)
                return {"success": False}

            pio_cmd, pio_env = get_platformio_command(PIO_HOME)
            env = os.environ.copy()
            env.update(pio_env)
            env.update(cache_env)
            env["TMP"] = str(TEMP_ROOT)
            env["TEMP"] = str(TEMP_ROOT)

            cmd = pio_cmd + [
                "run",
                "-t",
                "upload",
                f"--upload-port={actual_port}",
            ]

            session.process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(build_dir),
                env=env,
                creationflags=subprocess.CREATE_NO_WINDOW
                if sys.platform == "win32"
                else 0,
            )

            out_lines = []

            async def stream_u(pipe):
                while True:
                    line = await pipe.readline()
                    if not line:
                        break
                    txt = line.decode(errors="ignore").rstrip()
                    out_lines.append(txt)
                    await session.send(SessionPhase.START_UPLOAD, txt)

            await asyncio.gather(
                stream_u(session.process.stdout),
                stream_u(session.process.stderr),
            )

            code = await session.process.wait()
            session.process = None

            if code == 0:
                upload_success = True
                await session.send(SessionPhase.END_UPLOAD, "Upload complete")
            else:
                await session.send(SessionPhase.ERROR, "Upload failed", "error")

        # -----------------------------------------------------------
        # 5. CLEANUP + DONE
        # -----------------------------------------------------------
        cleanup_build_folder(build_dir)

        await session.send(SessionPhase.ALL_DONE, "All done")

        return {
            "success": True,
            "upload_success": upload_success,
            "message": "Process completed successfully",
            "session_id": session.id,
            "used_cache": not should_build if use_cache else False,
        }

    except Exception as e:
        await session.send(SessionPhase.ERROR, f"Unexpected error: {e}", "error")
        return {"success": False, "error": str(e)}

    finally:
        _active_sessions.pop(session.id, None)
