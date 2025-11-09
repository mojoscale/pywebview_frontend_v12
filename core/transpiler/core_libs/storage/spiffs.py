# __include_modules__ = {"espressif8266": "FS,SPIFFS", "espressif32": "FS"}
__include_internal_modules__ = {
    "espressif8266": "helpers/SPIFFSHelper",
    "espressif32": "helpers/SPIFFSHelper,SPIFFS",
}


__dependencies__ = ""


# __include_modules__ = {"espressif8266": "FS,SPIFFS", "espressif32": "FS"}
__include_internal_modules__ = {
    "espressif8266": "helpers/SPIFFSHelper",
    "espressif32": "helpers/SPIFFSHelper,SPIFFS",
}

__dependencies__ = ""


class File:
    """
    Represents a handle to an open file in the SPIFFS filesystem.

     class mirrors the behavior of the C++ `fs::File` class used with SPIFFS.
    You should not create a File directly; instead, use `SPIFFS.open(path, mode)`
    (or in the transpiler, `spiffs_open(path, mode)`).

    The File object allows reading, writing, and managing files in the
    SPIFFS or LittleFS filesystem on ESP32/ESP8266.
    """

    def __init__(self) -> None:
        """
        Creates an empty File object.
        Normally, you obtain a File from `spiffs_open()`.
        """
        __use_as_is__ = True
        pass

    def write(self, data: str) -> int:
        """
        Writes data to the file.

        Args:
            data (str): The data to write to the file.

        Returns:
            int: The number of bytes written.
        """
        __use_as_is__ = False
        __translation__ = (
            "{self}.write((const uint8_t*){data}.c_str(), strlen({data}.c_str()))"
        )
        return 0

    def print(self, data: str) -> int:
        """
        Writes data to the file (without a newline).

        Args:
            data (str): The text to print.

        Returns:
            int: The number of bytes written.
        """
        __use_as_is__ = False
        __translation__ = "{self}.print({data}.c_str())"
        return 0

    def println(self, data: str) -> int:
        """
        Writes data followed by a newline character to the file.

        Args:
            data (str): The text to print with a newline.

        Returns:
            int: The number of bytes written.
        """
        __use_as_is__ = False
        __translation__ = "{self}.println({data}.c_str())"
        return 0

    def available(self) -> int:
        """
        Returns the number of bytes available for reading.

        Returns:
            int: The number of bytes that can be read without blocking.
        """
        __use_as_is__ = False
        __translation__ = "{self}.available()"
        return 0

    def size(self) -> int:
        """
        Returns the total size of the file in bytes.

        Returns:
            int: The file size in bytes.
        """
        __use_as_is__ = False
        __translation__ = "{self}.size()"
        return 0

    def position(self) -> int:
        """
        Returns the current position of the file cursor.

        Returns:
            int: The current byte offset in the file.
        """
        __use_as_is__ = False
        __translation__ = "{self}.position()"
        return 0

    def seek(self, pos: int, mode: int = 0) -> bool:
        """
        Moves the file cursor to a specific position.

        Args:
            pos (int): The byte position to move to.
            mode (int, optional): The seek mode:
                0 = SeekSet (absolute)
                1 = SeekCur (relative)
                2 = SeekEnd (from end)

        Returns:
            bool: True if seek succeeded, False otherwise.
        """
        __use_as_is__ = False
        __translation__ = "{self}.seek({pos}, ({mode} == 1 ? SeekCur : ({mode} == 2 ? SeekEnd : SeekSet)))"
        return False

    def close(self) -> None:
        """
        Closes the file handle and releases resources.
        """
        __use_as_is__ = False
        __translation__ = "{self}.close()"
        pass

    def is_directory(self) -> bool:
        """
        Checks whether  File object refers to a directory.

        Returns:
            bool: True if  is a directory, False otherwise.
        """
        __use_as_is__ = False
        __translation__ = "{self}.isDirectory()"
        return False

    def name(self) -> str:
        """
        Returns the name (path) of the file.

        Returns:
            str: The file name or path.
        """
        __use_as_is__ = False
        __translation__ = "{self}.name()"
        return ""

    def rewind(self) -> None:
        """
        Resets the file cursor to the beginning of the file.
        """
        __use_as_is__ = False
        __translation__ = "{self}.seek(0, SeekSet)"
        pass

    def read_string(self) -> str:
        """
        Reads the file content as a string until EOF.

        Returns:
            str: The entire file content.
        """
        __use_as_is__ = False
        __translation__ = "{self}.readString()"
        return ""

    def peek(self) -> int:
        """
        Returns the next byte without advancing the file cursor.

        Returns:
            int: The next byte as an integer, or -1 if end of file.
        """
        __use_as_is__ = False
        __translation__ = "{self}.peek()"
        return -1

    def flush(self) -> None:
        """
        Forces any buffered data to be written to storage.
        """
        __use_as_is__ = False
        __translation__ = "{self}.flush()"
        pass


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


def spiffs_open(path: str, mode: str) -> File:
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
