__include_modules__ = "MHZ19"
__include_internal_modules__ = "helpers/sensors/MHZ19Helper"
__dependencies__ = "wifwaf/MH-Z19"


class MHZ19Sensor:
    def __init__(self, rx: int, tx: int, baud: int = 9600):
        """
        Initialize the MHZ19 CO₂ sensor.

        Args:
            stream: A serial stream object (e.g., Serial1 or SoftwareSerial).
        """
        __use_as_is__ = False
        __class_actual_type__ = "MHZ19"
        __pass_as__ = "pointer"
        __translation__ = "create_mhz19_sensor({rx}, {tx}, {baud})"
        __construct_with_equal_to__ = True

    def get_co2(self) -> int:
        """
        Get the measured CO₂ concentration.

        Returns:
            int: CO₂ value in ppm.
        """
        __use_as_is__ = False
        __translation__ = "{self}->getCO2()"

    def get_temperature(self) -> int:
        """
        Get the temperature reported by the sensor.

        Returns:
            int: Temperature in Celsius.
        """
        __use_as_is__ = False
        __translation__ = "{self}->getTemperature()"

    def get_accuracy(self) -> int:
        """
        Get the measurement accuracy level.

        Returns:
            int: Accuracy (unit depends on sensor calibration).
        """
        __use_as_is__ = False
        __translation__ = "{self}->getAccuracy()"

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
        __translation__ = "{self}->setRange({range_val})"

    def calibrate_zero(self) -> None:
        """
        Calibrate sensor assuming current ambient air has 400 ppm CO₂.
        """
        __use_as_is__ = False
        __translation__ = "{self}->calibrateZero()"

    def auto_calibration(self, enable: bool = True) -> None:
        """
        Enable or disable Automatic Baseline Calibration (ABC) mode.

        Args:
            enable (bool): True to enable ABC, False to disable.
        """
        __use_as_is__ = False
        __translation__ = "{self}->autoCalibration({enable})"
