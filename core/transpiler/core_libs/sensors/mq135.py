__include_modules__ = "MQ135"
__include_internal_modules__ = ""
__dependencies__ = ""


class MQ135Sensor:
    def __init__(self, pin: int):
        """
        Initialize the MQ135 sensor.

        Args:
            pin (int): The analog pin the MQ135 is connected to (e.g., A0 → 0)
        """
        __use_as_is__ = False
        __class_actual_type__ = "MQ135"
        __translation__ = "({1})"

    def get_correction_factor(self, temperature: float, humidity: float) -> float:
        """
        Return correction factor based on temperature and humidity.
        """
        __use_as_is__ = False
        __translation__ = "{0}.getCorrectionFactor({1}, {2})"

    def get_resistance(self) -> float:
        """
        Read the raw sensor resistance.
        """
        __use_as_is__ = False
        __translation__ = "{0}.getResistance()"

    def get_corrected_resistance(self, temperature: float, humidity: float) -> float:
        """
        Read corrected sensor resistance.
        """
        __use_as_is__ = False
        __translation__ = "{0}.getCorrectedResistance({1}, {2})"

    def get_ppm(self) -> float:
        """
        Return uncorrected PPM reading.
        """
        __use_as_is__ = False
        __translation__ = "{0}.getPPM()"

    def get_corrected_ppm(self, temperature: float, humidity: float) -> float:
        """
        Return PPM reading corrected for temperature and humidity.
        """
        __use_as_is__ = False
        __translation__ = "{0}.getCorrectedPPM({1}, {2})"

    def get_rzero(self) -> float:
        """
        Return RZero from current reading.
        """
        __use_as_is__ = False
        __translation__ = "{0}.getRZero()"

    def get_corrected_rzero(self, temperature: float, humidity: float) -> float:
        """
        Return corrected RZero based on temperature and humidity.
        """
        __use_as_is__ = False
        __translation__ = "{0}.getCorrectedRZero({1}, {2})"
