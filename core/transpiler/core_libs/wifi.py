__include_modules__ = "WiFi"
__include_internal_modules__ = "helpers/WiFiHelper"
__dependencies__ = ""


def wifi_connect(ssid: str, password: str, timeout: int) -> None:
    """
    Connects to a Wi-Fi network.

    Args:
        ssid (str): The SSID of the Wi-Fi network.
        password (str): The password for the network.
        timeout (int): Timeout in milliseconds.

    Returns:
        bool: True if connected successfully, else False.
    """
    __use_as_is__ = False
    __args__ = ["ssid", "password", "timeout"]
    __return_type__ = "bool"
    __translation__ = "WiFi.begin({0}, {1}); // Add timeout logic"
    raise NotImplementedError("wifi_connect is not implemented")


def wifi_begin(ssid: str, password: str) -> None:
    __use_as_is__ = False
    __translation__ = "WiFi.begin({0}, {1}); // Add timeout logic"


def wifi_is_connected() -> bool:
    """
    Checks Wi-Fi connection status.

    Returns:
        bool: True if connected to Wi-Fi.
    """
    __use_as_is__ = False
    __args__ = []
    __return_type__ = "bool"
    __translation__ = "WiFi.status() == WL_CONNECTED"
    raise NotImplementedError("wifi_is_connected is not implemented")


def wifi_localIP() -> str:
    __use_as_is__ = False
    __translation__ = "custom_wifi_helper_local_ip_to_string()"


def wifi_get_ip() -> str:
    """
    Retrieves the IP address assigned to the board.

    Returns:
        str: The local IP address as a string.
    """
    __use_as_is__ = False
    __args__ = []
    __return_type__ = "str"
    __translation__ = "WiFi.localIP().toString()"
    raise NotImplementedError("wifi_get_ip is not implemented")


def wifi_disconnect() -> None:
    """
    Disconnects from the Wi-Fi network.

    Returns:
        None
    """
    __use_as_is__ = False
    __args__ = []
    __return_type__ = "None"
    __translation__ = "WiFi.disconnect()"
    raise NotImplementedError("wifi_disconnect is not implemented")


def scan_network() -> list[str]:
    """
    Scan for available WiFi networks.

    Returns:
        list[str]: A list of SSIDs (network names) of nearby WiFi networks.

    Notes:
        - This method will call a native function: custom_wifi_helper_scan_wifi_networks().
        - It may block briefly while scanning completes.
    """
    __use_as_is__ = False
    __translation__ = "custom_wifi_helper_scan_wifi_networks()"


class WiFiClient:
    """
    A TCP client used for making WiFi-based socket connections (e.g., to MQTT/HTTP servers).
    """

    def __init__(self) -> None:
        """
        Initialize the client instance.
        """
        __use_as_is__ = False
        __class_actual_type__ = "WiFiClient"
        __translation__ = ""

        pass

    def connect(self, host: str, port: int) -> bool:
        """
        Connect to a TCP server.

        Args:
            host (str): Hostname or IP address.
            port (int): Port number.

        Returns:
            bool: True if connection succeeds.
        """
        __use_as_is__ = False
        __translation__ = "custom_wifi_client_helper_connect({0}, {1}, {2})"

        return False

    def write(self, data: str) -> int:
        """
        Send raw data to the server.

        Args:
            data (str): Data to send.

        Returns:
            int: Bytes written.
        """
        __use_as_is__ = False
        __translation__ = "custom_wifi_client_helper_write({0}, {1})"

        return 0

    def print(self, data: str) -> int:
        """
        Print data to the stream (human-readable).

        Args:
            data (str): Data to print.

        Returns:
            int: Bytes written.
        """
        __use_as_is__ = False
        __translation__ = "custom_wifi_client_helper_print({0}, {1})"

        return 0

    def println(self, data: str) -> int:
        """
        Print data followed by newline.

        Args:
            data (str): Data to print.

        Returns:
            int: Bytes written.
        """
        __use_as_is__ = False
        __translation__ = "custom_wifi_client_helper_println({0}, {1})"

        return 0

    def available(self) -> int:
        """
        Number of bytes available to read.

        Returns:
            int: Available byte count.
        """
        __use_as_is__ = True
        __translation__ = "{0}.available()"

        return 0

    def read(self) -> int:
        """
        Read a single byte/char.

        Returns:
            int: One byte as int.
        """
        __use_as_is__ = True
        __translation__ = "{0}.read()"

        return ""

    def read_bytes(self, buffer: str, length: int) -> int:
        """
        Read a fixed number of bytes into the provided buffer.

        Args:
            buffer (str): A string variable name that acts as the target buffer in generated code.
            length (int): Number of bytes to read.

        Returns:
            int: Number of bytes read.
        """
        __use_as_is__ = False
        __translation__ = "custom_wifi_client_helper_readBytes({0}, {1}, {2})"
        return 0

    def read_string(self) -> str:
        """
        Read all available bytes as a string.

        Returns:
            str: Entire stream as string.
        """
        __use_as_is__ = True
        __translation__ = "{0}.readString()"

        return ""

    def peek(self) -> int:
        """
        Peek at next byte without removing.

        Returns:
            int: Next byte as int.
        """
        __use_as_is__ = True
        __translation__ = "{0}.peek()"

        return ""

    def flush(self) -> None:
        """
        Wait for outgoing data to be sent.
        """
        __use_as_is__ = True
        __translation__ = "{0}.flush()"

        pass

    def stop(self) -> None:
        """
        Close the TCP connection.
        """
        __use_as_is__ = True
        __translation__ = "{0}.stop()"

        pass

    def connected(self) -> bool:
        """
        Check if still connected to server.

        Returns:
            bool: True if connected.
        """
        __use_as_is__ = True
        __translation__ = "{0}.connected()"

        return False
