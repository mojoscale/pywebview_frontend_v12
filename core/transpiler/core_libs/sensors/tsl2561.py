__include_modules__ = "Adafruit_TSL2561_U"
__dependencies__ = "adafruit/Adafruit TSL2561"
__include_internal_modules__ = "helpers/sensors/TSL2561Helper"


class TSL2561Sensor:
    def __init__(self, address: int):
        """
        Create a TSL2561 light sensor object.

        Args:
            address (int): I2C address of the sensor (0x29, 0x39, or 0x49).
        """
        __use_as_is__ = False
        __class_actual_type__ = "Adafruit_TSL2561_Unified"
        __translation__ = "({1})"

    def begin(self, address: int) -> bool:
        """
        Initialize the sensor with optional I2C address.

        Args:
            address (int): I2C address (default 0x39).

        Returns:
            bool: True if initialization succeeded.
        """
        __use_as_is__ = False
        __translation__ = "{0}.begin()"

    def enable_auto_range(self, enable: bool) -> None:
        """
        Enable or disable automatic gain range adjustment.

        Args:
            enable (bool): True to enable, False to disable.
        """
        __use_as_is__ = False
        __translation__ = "{0}.enableAutoRange({1})"

    def set_integration_time(self, integration_mode: int) -> None:
        """
        Set the integration time (exposure) for the light sensor.

        Args:
            integration_mode (int): One of:
                0 = 13ms,
                1 = 101ms,
                2 = 402ms
        """
        __use_as_is__ = False
        __translation__ = "{0}.setIntegrationTime({1})"

    def set_gain(self, gain_mode: int) -> None:
        """
        Set the gain mode of the light sensor.

        Args:
            gain_mode (int): 0 = 1x gain, 1 = 16x gain.
        """
        __use_as_is__ = False
        __translation__ = "{0}.setGain({1})"

    def get_luminosity(self) -> list[int]:
        """
        Read broadband and IR luminosity.

        Returns:
            list[int, int]: (broadband, ir) values.
        """
        __use_as_is__ = False
        __translation__ = "custom_tsl2561_helper_get_luminosity({0})"

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
        __translation__ = "{0}.calculateLux({1}, {2})"
