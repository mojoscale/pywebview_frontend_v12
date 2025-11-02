# __include_modules__ = {"espressif8266": "FS,SPIFFS", "espressif32": "FS"}
__include_internal_modules__ = {
    "espressif8266": "helpers/SPIFFSHelper",
    "espressif32": "helpers/SPIFFSHelper,SPIFFS",
}


__dependencies__ = ""


def spiffs_begin() -> bool:
    """
    Mounts the SPIFFS filesystem.

    Returns:
        bool: True if the filesystem is successfully mounted, False otherwise.
    """
    __use_as_is__ = False
    __translation__ = "SPIFFS.begin()"
    return False


def spiffs_end() -> None:
    """
    Unmounts the SPIFFS filesystem and releases resources.
    """
    __use_as_is__ = False
    __translation__ = "SPIFFS.end()"
    pass


def spiffs_format() -> bool:
    """
    Formats the SPIFFS filesystem.

    Returns:
        bool: True if formatting succeeds, False otherwise.
    """
    __use_as_is__ = False
    __translation__ = "SPIFFS.format()"
    return False


def spiffs_open(path: str, mode: str) -> None:
    """
    Opens a file in the SPIFFS filesystem.

    Args:
        path (str): Path to the file.
        mode (str): File mode (e.g., 'r', 'w', 'a').

    Returns:
        File object or None: File handle if successful, None otherwise.
    """
    __use_as_is__ = False
    __translation__ = "SPIFFS.open({path}.c_str(), {mode}.c_str())"
    return None


def spiffs_exists(path: str) -> bool:
    """
    Checks if a file or directory exists at the specified path.

    Args:
        path (str): Path to check.

    Returns:
        bool: True if the path exists, False otherwise.
    """
    __use_as_is__ = False
    __translation__ = "SPIFFS.exists({path}.c_str())"
    return False


def spiffs_remove(path: str) -> bool:
    """
    Deletes a file from the SPIFFS filesystem.

    Args:
        path (str): Path of the file to delete.

    Returns:
        bool: True if file is successfully removed, False otherwise.
    """
    __use_as_is__ = False
    __translation__ = "SPIFFS.remove({path}.c_str())"
    return False


def spiffs_rename(src: str, dest: str) -> bool:
    """
    Renames or moves a file.

    Args:
        src (str): Source file path.
        dest (str): Destination file path.

    Returns:
        bool: True if successful, False otherwise.
    """
    __use_as_is__ = False
    __translation__ = "SPIFFS.rename({src}.c_str(), {dest}.c_str())"
    return False


def spiffs_mkdir(path: str) -> bool:
    """
    Creates a directory in the SPIFFS filesystem.

    Args:
        path (str): Directory path.

    Returns:
        bool: True if successful, False otherwise.
    """
    __use_as_is__ = False
    __translation__ = "SPIFFS.mkdir({path}.c_str())"
    return False


def spiffs_rmdir(path: str) -> bool:
    """
    Removes a directory from the SPIFFS filesystem.

    Args:
        path (str): Directory path.

    Returns:
        bool: True if successful, False otherwise.
    """
    __use_as_is__ = False
    __translation__ = "SPIFFS.rmdir({path}.c_str())"
    return False


def spiffs_used_bytes() -> int:
    """
    Returns the number of bytes currently used in the SPIFFS filesystem.

    Returns:
        int: Number of used bytes.
    """
    __use_as_is__ = False
    __translation__ = "custom_spiffs_helper_get_used_bytes()"
    return 0


def spiffs_total_bytes() -> int:
    """
    Returns the total size of the SPIFFS filesystem.

    Returns:
        int: Total number of bytes available.
    """
    __use_as_is__ = False
    __translation__ = "custom_spiffs_helper_get_total_bytes()"
    return 0


def spiffs_free_bytes() -> int:
    """
    Returns the number of free bytes in the SPIFFS filesystem.

    Returns:
        int: Number of free bytes available.
    """
    __use_as_is__ = False
    __translation__ = "(custom_spiffs_helper_get_total_bytes() - custom_spiffs_helper_get_used_bytes())"
    return 0


def spiffs_info() -> dict[str, str]:
    """
    Prints or returns general information about the SPIFFS filesystem.
    (Custom implementation required)
    """
    __use_as_is__ = False
    __translation__ = "custom_spiffs_helper_get_spiffs_info()"
    return None
