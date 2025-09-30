
__include_modules__ =  {"espressif8266":"LittleFS", 
"espressif32":"LittleFS"}


__include_internal_modules__ = {"espressif8266":"helpers/LittleFSHelperESP8266", 
"espressif32":"helpers/LittleFSHelperESP32"}



__dependencies__ = ""



class File:
    """
    A file object used for reading from and writing to a filesystem.
    """

    def __init__(self) -> None:
        __use_as_is__ = True
        pass


    def __print__(self):
        __use_as_is__=False

        __translation__ = "custom_littlefs_helper_file_to_string({0})"

    def write(self, data: str) -> int:
        __use_as_is__ = False
        __translation__ = "{0}.write((const uint8_t*)({1}).c_str(), ({1}).length())"
        return 0

    def print(self, data: str) -> int:
        __use_as_is__ = False
        __translation__ = "{0}.print({1}.c_str())"
        return 0

    def println(self, data: str) -> int:
        __use_as_is__ = False
        __translation__ = "{0}.println({1}.c_str())"
        return 0

    def read(self) -> str:
        __use_as_is__ = False
        __translation__ = "{0}.read()"
        return ""

    def readString(self) -> str:
        __use_as_is__ = False
        __translation__ = "{0}.readString()"
        return ""

    def readBytes(self, length: int) -> str:
        """
        Read a fixed number of bytes from the file.

        Returns:
            str: Data read.
        """
        __use_as_is__ = True
        
        return ""

    def readBytesUntil(self, terminator: str, length: int) -> str:
        """
        Read bytes until a terminator or length is reached.

        Returns:
            str: Data read.
        """
        __use_as_is__ = False
        __translation__ = "{0}.readBytesUntil({1}.c_str(), {2})"
        return ""

    def peek(self) -> str:
        """
        Peek at the next byte without moving the file pointer.
        """
        __use_as_is__ = True
        
        return ""

    def available(self) -> int:
        __use_as_is__ = True

        return 0

    def seek(self, pos: int) -> bool:
        __use_as_is__ = True
        
        return False

    def position(self) -> int:
        """
        Get the current position of the file pointer.
        """
        __use_as_is__ = True
        
        return 0

    def flush(self) -> None:
        __use_as_is__ = True
        
        return None

    def close(self) -> None:
        __use_as_is__ = True
        return None

    def isDirectory(self) -> bool:
        __use_as_is__ = True
        return False

    def name(self) -> str:
        __use_as_is__ = True
        return ""

    def size(self) -> int:
        """
        Get the size of the file in bytes.
        """
        __use_as_is__ = True
        return 0

    def getWriteError(self) -> bool:
        """
        Return True if a write error occurred.
        """
        __use_as_is__ = True
        return False

    def clearWriteError(self) -> None:
        """
        Clear any write error flags.
        """
        __use_as_is__ = True
        return None

    def openNextFile(self) -> File:
        """
        Return the next file in a directory (if this is a directory).
        """
        __use_as_is__ = True
        return File()






def littlefs_begin(format_on_fail: bool) -> bool:
    """
    Mounts the LittleFS filesystem.

    Args:
        format_on_fail (bool): Whether to format the FS if mounting fails.

    Returns:
        bool: True if successful. (works only on ESP32)
    """
    __use_as_is__ = False
    #__translation__ = "LittleFS.begin({0})"
    __translation__ = {"espressif8266":"LittleFS.begin()", 
"espressif32":"LittleFS.begin({0})"}
    return False


def littlefs_end() -> None:
    """
    Unmounts the filesystem and releases resources.
    """
    __use_as_is__ = False
    __translation__ = "LittleFS.end()"
    pass


def littlefs_format() -> bool:
    """
    Formats the filesystem.

    Returns:
        bool: True if successful.
    """
    __use_as_is__ = False
    __translation__ = "LittleFS.format()"
    return False


def littlefs_open(path: str, mode: str) -> File:
    """
    Opens a file.

    Args:
        path (str): Path to file.
        mode (str): Access mode (e.g., 'r', 'w').

    Returns:
        File or None
    """
    __use_as_is__ = False
    __translation__ = "LittleFS.open({0}.c_str(), {1}.c_str())"
    return None


def littlefs_exists(path: str) -> bool:
    """
    Checks whether a path exists.

    Returns:
        bool
    """
    __use_as_is__ = False
    __translation__ = "LittleFS.exists({0}.c_str())"
    return False


def littlefs_remove(path: str) -> bool:
    """
    Deletes a file.

    Returns:
        bool
    """
    __use_as_is__ = False
    __translation__ = "LittleFS.remove({0}.c_str())"
    return False


def littlefs_rename(src: str, dest: str) -> bool:
    """
    Renames or moves a file.

    Returns:
        bool
    """
    __use_as_is__ = False
    __translation__ = "LittleFS.rename({0}.c_str(), {1}.c_str())"
    return False


def littlefs_mkdir(path: str) -> bool:
    """
    Creates a directory.

    Returns:
        bool
    """
    __use_as_is__ = False
    __translation__ = "LittleFS.mkdir({0}.c_str())"
    return False


def littlefs_rmdir(path: str) -> bool:
    """
    Removes a directory.

    Returns:
        bool
    """
    __use_as_is__ = False
    __translation__ = "LittleFS.rmdir({0}.c_str())"
    return False


def littlefs_total_bytes() -> int:
    """
    Returns total FS size in bytes.

    Returns:
        int
    """
    __use_as_is__ = False
    __translation__ = "LittleFS.totalBytes()"
    return 0


def littlefs_used_bytes() -> int:
    """
    Returns used FS size in bytes.

    Returns:
        int
    """
    __use_as_is__ = False
    __translation__ = "LittleFS.usedBytes()"
    return 0


def littlefs_free_bytes() -> int:
    """
    Returns free space in bytes.

    Returns:
        int
    """
    __use_as_is__ = False
    __translation__ = "LittleFS.totalBytes() - LittleFS.usedBytes()"
    return 0


def littlefs_info() -> dict[str, str]:
    """
    Returns filesystem info.

    Returns:
        dict with status, used, total, free
    """
    __use_as_is__ = False
    __translation__ = "custom_littlefs_helper_get_littlefs_info()"
    return None


