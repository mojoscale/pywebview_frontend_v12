import os
import json
import sys
from pathlib import Path
import importlib.resources as pkg_resources


import requests

APP_WINDOW_NAME = "Mojoscale IDE"

APP_FOLDER_NAME = ".mojoscale"

AVAILABLE_BOARDS_PATH = os.path.join(os.path.dirname(__file__), "available_boards.json")


STARTER_CODE = """

def setup()->None:
    pass 


def loop()->None:
    pass

"""


def get_app_dir():
    base_dir = os.path.expanduser("~")

    return os.path.join(base_dir, APP_FOLDER_NAME)


def check_or_create_app_dir():
    """
    Ensure the given folder exists.
    - If it exists already, return None.
    - If it does not exist, create it and return the created path.
    """
    path = get_app_dir()
    if os.path.isdir(path):
        return None
    else:
        os.makedirs(path, exist_ok=True)
        return path


def get_available_platforms():
    """Return list of unique platform values from available_boards.json."""
    file_path = AVAILABLE_BOARDS_PATH

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"{file_path} not found")

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Expecting data to be a list of dicts
    platforms = {item.get("platform") for item in data if "platform" in item}
    return sorted(platforms)  # sorted list of unique values


def get_available_boards():
    file_path = AVAILABLE_BOARDS_PATH
    with open(file_path, "r", encoding="utf-8-sig") as f:
        boards = json.load(f)

    allowed_platforms = {"espressif32", "espressif8266"}
    filtered = [
        b for b in boards if str(b.get("platform", "")).lower() in allowed_platforms
    ]

    return sorted({f"{b['name']} ({b['id']})" for b in filtered})


"""def get_available_boards():
    # assuming available_boards.json is inside package core/
    with pkg_resources.files("core").joinpath("available_boards.json").open(
        "r", encoding="utf-8-sig"
    ) as f:
        boards = json.load(f)
    return sorted({f"{b['name']} ({b['id']})" for b in boards})"""


def get_platform_for_board_id(board_id: str) -> str:
    """
    Looks up the platform name for a given board ID from available_boards.json.

    Args:
        board_id (str): The board ID to search for.
        json_path (str): Path to the available_boards.json file.

    Returns:
        str: The platform name (e.g., "espressif32"), or None if not found.
    """
    json_path = AVAILABLE_BOARDS_PATH
    with open(json_path, "r", encoding="utf-8-sig") as f:
        boards = json.load(f)

    for board in boards:
        if board.get("id") == board_id:
            return board.get("platform")

    return None


def get_resource_path(relative_path):
    """Get absolute path to resource for both dev and PyInstaller"""
    if getattr(sys, "frozen", False):
        base_path = Path(sys._MEIPASS)
    else:
        base_path = Path(__file__).parent

    # Try direct path first
    file_path = base_path / relative_path
    if file_path.exists():
        return str(file_path)

    # Try parent directory (common in one-file mode)
    file_path = base_path.parent / relative_path
    return str(file_path)


def get_bundled_python_exe():
    """
    Get the correct Python executable for both dev and packaged environments.
    """
    # If we're in a packaged app (Nuitka, PyInstaller, etc.)
    if hasattr(sys, "_MEIPASS"):
        # In packaged mode, use the bundled Python
        if sys.platform == "win32":
            # Windows packaged app - Python should be in the same directory
            python_exe = os.path.join(os.path.dirname(sys.executable), "python.exe")
            if os.path.exists(python_exe):
                return python_exe
        # Fallback to sys.executable (the packaged app itself might be Python)
        return sys.executable
    else:
        # Development mode - use current Python
        return sys.executable


def get_all_platformio_boards(output_folder: str):
    """
    Fetches all available PlatformIO boards as JSON
    and stores them inside available_boards.json in the given folder.

    :param output_folder: Path to the folder where JSON should be saved.
    """

    # Ensure folder exists
    os.makedirs(output_folder, exist_ok=True)

    output_file = AVAILABLE_BOARDS_PATH

    url = "https://api.platformio.org/v2/boards"

    try:
        print("📡 Downloading PlatformIO board definitions...")
        response = requests.get(url, timeout=20)

        if response.status_code != 200:
            raise RuntimeError(
                f"PlatformIO API returned status code {response.status_code}"
            )

        boards = response.json()

        # Save JSON nicely formatted
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(boards, f, indent=2, ensure_ascii=False)

        print(f"✅ Saved {len(boards)} boards to: {output_file}")

    except Exception as e:
        print("❌ Failed to retrieve PlatformIO boards:", str(e))
        raise


def get_mcu_by_board_name(board_name):
    """
    Return the MCU string for a given board name or id.
    Matches against:
        - id
        - name
    Match is case-insensitive.
    """
    boards_json_path = AVAILABLE_BOARDS_PATH
    board_name = board_name.strip().lower()

    with open(boards_json_path, "r", encoding="utf-8") as f:
        boards = json.load(f)

    for b in boards:
        if b.get("id", "").lower() == board_name:
            return b.get("mcu")
        if b.get("name", "").lower() == board_name:
            return b.get("mcu")

    return None  # Not found
