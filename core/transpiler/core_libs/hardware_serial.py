# core_libs/HardwareSerial.py

"""
HardwareSerial core stub for Arduino-compatible boards (AVR, ESP8266, ESP32, RP2040).

This class represents a hardware UART interface used for serial communication.
It provides methods to configure baud rate, read and write data, and manage
the serial buffer.

Compatible with the built-in Arduino `Serial`, `Serial1`, `Serial2`, etc.
"""

__include_modules__ = "HardwareSerial"
__include_internal_modules__ = ""
__dependencies__ = ""


class HardwareSerial:
    """
    Stub representation of Arduino's HardwareSerial class.
    Used for serial communication with external devices or debug consoles.
    """

    def __init__(self, port_id: int = 0):
        """
        Initialize a HardwareSerial interface.

        Args:
            port_id (int): UART port index (0 for Serial, 1 for Serial1, etc.).
        """
        __use_as_is__ = False
        __class_actual_type__ = "HardwareSerial"
        __translation__ = "HardwareSerial({1})"
        __construct_with_equal_to__ = True

    def begin(self, baud: int, config: int = 0x06) -> None:
        """
        Begin serial communication with the specified baud rate and configuration.

        Args:
            baud (int): Baud rate (e.g., 9600, 115200).
            config (int): Serial configuration constant (e.g., SERIAL_8N1 = 0x06).

        Example:
            ```python
            serial = HardwareSerial(1)
            serial.begin(115200)
            ```
        """
        __use_as_is__ = False
        __translation__ = "{0}.begin({1}, {2})"

    def end(self) -> None:
        """
        Stop serial communication.
        """
        __use_as_is__ = False
        __translation__ = "{0}.end()"

    def available(self) -> int:
        """
        Get number of bytes available to read from the buffer.

        Returns:
            int: Number of available bytes.
        """
        __use_as_is__ = False
        __translation__ = "{0}.available()"
        return 0

    def available_for_write(self) -> int:
        """
        Get number of bytes available for writing to the transmit buffer.

        Returns:
            int: Number of writable bytes.
        """
        __use_as_is__ = False
        __translation__ = "{0}.availableForWrite()"
        return 0

    def read(self) -> int:
        """
        Read one byte from the serial buffer.

        Returns:
            int: The next byte, or -1 if no data is available.
        """
        __use_as_is__ = False
        __translation__ = "{0}.read()"
        return -1

    def peek(self) -> int:
        """
        Return the next byte without removing it from the buffer.

        Returns:
            int: Next byte, or -1 if none.
        """
        __use_as_is__ = False
        __translation__ = "{0}.peek()"
        return -1

    def flush(self) -> None:
        """
        Wait for outgoing data to be transmitted.
        """
        __use_as_is__ = False
        __translation__ = "{0}.flush()"

    def write(self, value: int) -> int:
        """
        Write a single byte to the serial output.

        Args:
            value (int): Byte value to send (0–255).

        Returns:
            int: Number of bytes written (usually 1).
        """
        __use_as_is__ = False
        __translation__ = "{0}.write({1})"
        return 1

    def print(self, value) -> None:
        """
        Print a value as text to the serial output.

        Args:
            value: Any printable type (str, int, float).
        """
        __use_as_is__ = False
        __translation__ = "{0}.print({1})"

    def println(self, value) -> None:
        """
        Print a value followed by a newline.

        Args:
            value: Any printable type (str, int, float).
        """
        __use_as_is__ = False
        __translation__ = "{0}.println({1})"

    def set_timeout(self, timeout_ms: int) -> None:
        """
        Set read timeout (used by readBytes, readString, etc.).

        Args:
            timeout_ms (int): Timeout in milliseconds.
        """
        __use_as_is__ = False
        __translation__ = "{0}.setTimeout({1})"
