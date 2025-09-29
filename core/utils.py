import os


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
