__include_modules__ = "MHZ19"
__include_internal_modules__ = "helpers/sensors/MHZ19Helper"
__dependencies__ = "wifwaf/MH-Z19"


class MHZ19Sensor:
    def __init__(self, stream: HardwareSerial):
        """
        Initialize the MHZ19 CO₂ sensor.

        Args:
            stream: A serial stream object (e.g., Serial1 or SoftwareSerial).
        """
        __use_as_is__ = False
        __class_actual_type__ = "MHZ19"
        __translation__ = "custom_mhz19_helper_create_mhz19({1})"
        __construct_with_equal_to__ = True

    def get_co2(self) -> int:
        """
        Get the measured CO₂ concentration.

        Returns:
            int: CO₂ value in ppm.
        """
        __use_as_is__ = False
        __translation__ = "{0}.getCO2()"

    def get_temperature(self) -> int:
        """
        Get the temperature reported by the sensor.

        Returns:
            int: Temperature in Celsius.
        """
        __use_as_is__ = False
        __translation__ = "{0}.getTemperature()"

    def get_accuracy(self) -> int:
        """
        Get the measurement accuracy level.

        Returns:
            int: Accuracy (unit depends on sensor calibration).
        """
        __use_as_is__ = False
        __translation__ = "{0}.getAccuracy()"

    def set_range(self, range_val: int) -> None:
        """
        Set the CO₂ measurement range of the MH-Z19 sensor.

        Args:
            range_val (int): Desired measurement range in parts per million (ppm).
                Valid values are typically:
                    - 2000   → 0–2000 ppm
                    - 5000   → 0–5000 ppm
                    - 10000  → 0–10000 ppm (only on supported models)

        Notes:
            - The range is stored in the sensor’s non-volatile memory.
            - Changing the range may require recalibration.
            - Unsupported values will be ignored or may yield invalid readings.
        """
        __use_as_is__ = False
        __translation__ = "{0}.setRange({1})"

    def calibrate_zero(self) -> None:
        """
        Calibrate sensor assuming current ambient air has 400 ppm CO₂.
        """
        __use_as_is__ = False
        __translation__ = "{0}.calibrateZero()"

    def auto_calibration(self, enable: bool) -> None:
        """
        Enable or disable Automatic Baseline Calibration (ABC) mode.

        Args:
            enable (bool): True to enable ABC, False to disable.
        """
        __use_as_is__ = False
        __translation__ = "{0}.autoCalibration({1})"
