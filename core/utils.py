import os
import json
import sys
from pathlib import Path

APP_WINDOW_NAME = "Mojoscale IDE"

APP_FOLDER_NAME = ".mojoscale_main_folder"


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
    file_path = os.path.join(os.path.dirname(__file__), "available_boards.json")

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"{file_path} not found")

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Expecting data to be a list of dicts
    platforms = {item.get("platform") for item in data if "platform" in item}
    return sorted(platforms)  # sorted list of unique values


def get_available_boards():
    file_path = os.path.join(os.path.dirname(__file__), "available_boards.json")
    with open(file_path, "r", encoding="utf-8-sig") as f:
        boards = json.load(f)

    return sorted({f"{b['name']} ({b['id']})" for b in boards})


def get_platform_for_board_id(board_id: str) -> str:
    """
    Looks up the platform name for a given board ID from available_boards.json.

    Args:
        board_id (str): The board ID to search for.
        json_path (str): Path to the available_boards.json file.

    Returns:
        str: The platform name (e.g., "espressif32"), or None if not found.
    """
    json_path = os.path.join(os.path.dirname(__file__), "available_boards.json")
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
    # 1. If app ships with its own env folder, use that first
    local_env = os.path.join(os.path.dirname(__file__), "env", "Scripts", "python.exe")
    if os.path.exists(local_env):
        return local_env

    # 2. Otherwise, always use current interpreter
    return sys.executable
