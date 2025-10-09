__include_modules__ = "MQ2"
__include_internal_modules__ = "helpers/sensors/MQ2Helper"
__dependencies__ = "https://github.com/labay11/MQ-2-sensor-library.git"


class MQ2Sensor:
    """
    MQ2 gas sensor abstraction using the Labay11/MQ-2-sensor-library.

    Provides methods for reading concentrations of LPG, CO, and Smoke.
    """

    def __init__(self, pin: int):
        """
        Initialize the MQ2 sensor.

        Args:
            pin (int): The analog pin connected to the sensor (e.g., A0 → 0).
        """
        __use_as_is__ = False
        __class_actual_type__ = "MQ2"
        __translation__ = "({1})"

    def begin(self) -> None:
        """
        Initialize the MQ2 sensor hardware and calibration routines.
        Must be called before reading data.
        """
        __use_as_is__ = False
        __translation__ = "{0}.begin()"

    def close(self) -> None:
        """
        Stop the MQ2 sensor and clear calibration data.
        """
        __use_as_is__ = False
        __translation__ = "{0}.close()"

    def read(self, debug: bool) -> list[float]:
        """
        Read all gas concentrations from the sensor.

        Args:
            debug (bool): If True, prints internal readings via Serial.

        Returns:
            list[float]: [LPG, CO, Smoke] in ppm.
        """
        __use_as_is__ = False
        __translation__ = "{0}.read({1})"
        return [0.0, 0.0, 0.0]

    def read_lpg(self) -> float:
        """
        Read LPG concentration in ppm.

        Returns:
            float: LPG concentration.
        """
        __use_as_is__ = False
        __translation__ = "{0}.readLPG()"
        return 0.0

    def read_co(self) -> float:
        """
        Read CO concentration in ppm.

        Returns:
            float: CO concentration.
        """
        __use_as_is__ = False
        __translation__ = "{0}.readCO()"
        return 0.0

    def read_smoke(self) -> float:
        """
        Read smoke concentration in ppm.

        Returns:
            float: Smoke concentration.
        """
        __use_as_is__ = False
        __translation__ = "{0}.readSmoke()"
        return 0.0
