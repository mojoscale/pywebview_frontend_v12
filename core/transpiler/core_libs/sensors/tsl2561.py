__include_modules__ = "Adafruit_TSL2561_U"
__dependencies__ = "adafruit/Adafruit TSL2561"
__include_internal_modules__ = "helpers/sensors/TSL2561Helper"


class TSL2561Sensor:
    def __init__(self, address: int = 0x39):
        """
        Create a TSL2561 light sensor object.

        Args:
            address (int): I2C address of the sensor (0x29, 0x39, or 0x49).
        """
        __use_as_is__ = False
        __class_actual_type__ = "Adafruit_TSL2561_Unified"
        __translation__ = "({address})"

    def begin(self) -> bool:
        """
        Initialize the sensor.

        Returns:
            bool: True if initialization succeeded.
        """
        __use_as_is__ = False
        __translation__ = "{self}.begin()"

    def enable_auto_range(self, enable: bool) -> None:
        """
        Enable or disable automatic gain range adjustment.
        """
        __use_as_is__ = False
        __translation__ = "{self}.enableAutoRange({enable})"

    def set_integration_time(self, integration_mode: int) -> None:
        """
        Set the integration time (exposure).

        Args:
            integration_mode (int): One of:
                0 = 13ms,
                1 = 101ms,
                2 = 402ms
        """
        __use_as_is__ = False
        __translation__ = (
            "custom_tsl2561_helper_set_integration_time(&{self}, {integration_mode})"
        )

    def set_gain(self, gain_mode: int) -> None:
        """
        Set gain mode.

        Args:
            gain_mode (int): 0 = 1x gain, 1 = 16x gain.
        """
        __use_as_is__ = False
        __translation__ = "custom_tsl2561_helper_set_gain(&{self}, {gain_mode})"

    def get_luminosity(self) -> list[int]:
        """
        Read broadband and IR luminosity.

        Returns:
            list[int, int]: (broadband, ir) values.
        """
        __use_as_is__ = False
        __translation__ = "custom_tsl2561_helper_get_luminosity(&{self})"

    def calculate_lux(self, broadband: int, ir: int) -> int:
        """
        Calculate lux value from given channel readings.

        Args:
            broadband (int): Channel 0 (visible + IR).
            ir (int): Channel 1 (IR only).

        Returns:
            int: Calculated lux value.
        """
        __use_as_is__ = False
        __translation__ = "{self}.calculateLux({broadband}, {ir})"
