__include_modules__ = "BH1750"
__dependencies__ = "claws/BH1750"
__include_internal_modules__ = "helpers/sensors/BH1750Helper"


class BH1750Sensor:
    def __init__(self, address: int):
        """
        Create a BH1750 light sensor object.

        Args:
            address (int): I2C address of the sensor. Default is 0x23.
        """
        __use_as_is__ = False
        __class_actual_type__ = "BH1750"
        __translation__ = "({1})"

    def begin(self, mode_index: int = 1, address: int = 0x23) -> bool:
        """
        Initialize the BH1750 sensor instance with selected measurement mode and I2C address.

        Args:
            mode_index (int): Measurement mode:
                1 = CONTINUOUS_HIGH_RES_MODE
                2 = CONTINUOUS_HIGH_RES_MODE_2
                3 = CONTINUOUS_LOW_RES_MODE
                4 = ONE_TIME_HIGH_RES_MODE
                5 = ONE_TIME_HIGH_RES_MODE_2
                6 = ONE_TIME_LOW_RES_MODE
            address (int): I2C address (0x23 = 35 by default)

        Returns:
            bool: True if initialization succeeded.

        Note:
            Uses internal helper `bh1750_map_mode(mode_index)` to convert to BH1750::Mode.
        """
        __use_as_is__ = False
        __translation__ = "custom_bh1750_helper_begin({0}, {1}, {2})"

    def configure(self, mode: int) -> bool:
        """
        Change measurement mode of the sensor.

        Args:
            mode (int): One of the defined measurement mode constants.

        Returns:
            bool: True if configuration succeeded.
        """
        __use_as_is__ = False
        __translation__ = "{0}.configure({1})"

    def set_mtreg(self, mtreg: int) -> bool:
        """
        Set MTreg register value for sensitivity control (31–254).

        Args:
            mtreg (int): Value between 31 and 254.

        Returns:
            bool: True if register was set successfully.
        """
        __use_as_is__ = False
        __translation__ = "{0}.setMTreg({1})"

    def measurement_ready(self, max_wait: bool) -> bool:
        """
        Check whether a measurement is ready.

        Args:
            max_wait (bool): If True, waits up to max measurement time.

        Returns:
            bool: True if data is ready to read.
        """
        __use_as_is__ = False
        __translation__ = "{0}.measurementReady({1})"

    def read_light_level(self) -> float:
        """
        Read the measured light level in lux.

        Returns:
            float: Light level in lux.
        """
        __use_as_is__ = False
        __translation__ = "{0}.readLightLevel()"
