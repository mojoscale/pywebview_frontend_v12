__include_modules__ = ""
__include_internal_modules__ = "helpers/sensors/MQ2Helper"
__dependencies__ = ""


class MQ2Sensor:
    def __init__(self, pin: int):
        """
        Initialize the MQ2 sensor.

        Args:
            pin (int): The analog pin the MQ2 is connected to (e.g., A0 → 0)
        """
        __use_as_is__ = False
        __class_actual_type__ = "MQ2"
        __translation__ = "({1})"

    def calibrate_r0(self, samples: int, delay_ms: int) -> None:
        """
        Calibrate R0 using clean air.

        Args:
            samples (int): Number of samples to average.
            delay_ms (int): Delay between samples.
        """
        __use_as_is__ = True

    def set_r0(self, r0: float) -> None:
        """
        Manually set the R0 (clean air resistance).
        """
        __use_as_is__ = True

    def get_r0(self) -> float:
        """
        Get the current R0 value.
        """
        __use_as_is__ = True

    def read_rs(self) -> float:
        """
        Read current Rs (sensor resistance in current gas).
        """
        __use_as_is__ = True

    def read_ratio(self) -> float:
        """
        Return Rs/R0.
        """
        __use_as_is__ = True

    def get_ppm(self, a: float, b: float) -> float:
        """
        Compute PPM using the formula: ppm = a * (Rs/R0)^b
        """
        __use_as_is__ = True

    def read(self, debug: bool) -> list[float]:
        """
        Read all gas concentrations. Debug may print internally.
        """
        __use_as_is__ = False
        __translation__ = "{0}.read({1})"

    def read_lpg(self) -> float:
        """
        Read LPG concentration in ppm.
        """
        __use_as_is__ = False
        __translation__ = "{0}.readLPG()"

    def read_co(self) -> float:
        """
        Read CO concentration in ppm.
        """
        __use_as_is__ = False
        __translation__ = "{0}.readCO()"

    def read_smoke(self) -> float:
        """
        Read Smoke concentration in ppm.
        """
        __use_as_is__ = False
        __translation__ = "{0}.readSmoke()"
