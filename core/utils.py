import os
import json

APP_WINDOW_NAME = "Mojoscale IDE"

APP_FOLDER_NAME = ".mojoscale_main_folder"


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
