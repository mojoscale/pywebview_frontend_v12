__include_modules__ = "OneWire"
__include_internal_modules__ = "helpers/OneWireHelper"
__dependencies__ = "paulstoffregen/OneWire@^2.3.4"


class OneWire:
    """
    A Python-like abstraction for the OneWire communication protocol.
    Supports devices like DS18B20 and other 1-wire sensors.
    """

    def __init__(self, pin: int) -> None:
        """
        Initialize the OneWire bus on a specific GPIO pin.

        Args:
            pin (int): GPIO pin number.
        """
        __use_as_is__ = False
        __class_actual_type__ = "OneWire"
        __translation__ = "({1})"

    def reset(self) -> bool:
        """
        Reset all devices on the OneWire bus.

        Returns:
            bool: True if devices respond, False otherwise.
        """
        __use_as_is__ = False
        __translation__ = "{0}.reset()"
        return True

    def write(self, value: int, power: bool = False) -> None:
        """
        Write a single byte to the OneWire bus.

        Args:
            value (int): Byte to write.
            power (bool): If True, enables strong pull-up for power.
        """
        __use_as_is__ = False
        __translation__ = "{0}.write({1}, {2})"
        pass

    def write_bytes(self, data: list[int], power: bool = False) -> None:
        """
        Write multiple bytes to the OneWire bus.

        Args:
            data (list[int]): List of bytes to write.
            power (bool): If True, enables strong pull-up for power.
        """
        __use_as_is__ = False
        __translation__ = "{0}.write_bytes({1}, {2})"
        pass

    def read(self) -> int:
        """
        Read a single byte from the OneWire bus.

        Returns:
            int: Byte read.
        """
        __use_as_is__ = False
        __translation__ = "{0}.read()"
        return 0

    def read_bytes(self, count: int) -> list[int]:
        """
        Read multiple bytes from the OneWire bus.

        Args:
            count (int): Number of bytes to read.

        Returns:
            list[int]: Bytes read.
        """
        __use_as_is__ = False
        __translation__ = "custom_onewire_helper_read_bytes({0}, {1})"
        return [0] * count

    def select(self, rom_code: list[int]) -> None:
        """
        Select a specific device on the bus using its ROM address.

        Args:
            rom_code (list[int]): 8-byte unique ROM address.
        """
        __use_as_is__ = False
        __translation__ = "{0}.select({1})"
        pass

    def skip(self) -> None:
        """
        Skip ROM selection and address all devices.
        """
        __use_as_is__ = False
        __translation__ = "{0}.skip()"
        pass

    def reset_search(self) -> None:
        """
        Reset the internal state used by search().
        """
        __use_as_is__ = False
        __translation__ = "{0}.reset_search()"
        pass

    def search(self) -> list[int]:
        """
        Search for the next device on the OneWire bus.

        Returns:
            list[int] or None: ROM address (8-byte) or None if no more devices.
        """
        __use_as_is__ = False
        __translation__ = "custom_onewire_helper_search({0})"
        return None
