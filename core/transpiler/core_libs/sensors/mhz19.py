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

    def retrieve_data(self) -> int:
        """
        Request sensor to update internal values.

        Returns:
            int: Result code from MHZ19_RESULT enum (e.g., 0 for OK, 5 for TIMEOUT).
        """
        __use_as_is__ = False
        __translation__ = "{0}.retrieveData()"

    def get_co2(self) -> int:
        """
        Get the measured CO₂ concentration.

        Returns:
            int: CO₂ value in ppm.
        """
        __use_as_is__ = False
        __translation__ = "{0}.getCO2()"

    def get_min_co2(self) -> int:
        """
        Get the minimum possible CO₂ value (requires further processing).

        Returns:
            int: Minimum CO₂ value.
        """
        __use_as_is__ = False
        __translation__ = "{0}.getMinCO2()"

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

    def set_range(self, range_val: int) -> int:
        """
        Set the CO2 sensing range.

        Args:
            range_val (int): One of:
                - 0: MHZ19_RANGE_1000
                - 1: MHZ19_RANGE_2000
                - 2: MHZ19_RANGE_3000
                - 3: MHZ19_RANGE_5000
                - 4: MHZ19_RANGE_10000
        Returns:
            int: Result code from MHZ19_RESULT enum.
        """
        __use_as_is__ = False
        __translation__ = "{0}.setRange({1})"

    def calibrate_zero(self) -> None:
        """
        Calibrate sensor assuming current ambient air has 400 ppm CO₂.
        """
        __use_as_is__ = False
        __translation__ = "{0}.calibrateZero()"

    def calibrate_span(self, span: int) -> None:
        """
        Calibrate span (high-end point) using known CO₂ concentration.

        Args:
            span (int): Known CO₂ concentration in ppm (e.g., 2000).
        """
        __use_as_is__ = False
        __translation__ = "{0}.calibrateSpan({1})"

    def set_auto_calibration(self, mode: bool) -> None:
        """
        Enable or disable automatic baseline calibration.

        Args:
            mode (bool): True to enable, False to disable.
        """
        __use_as_is__ = False
        __translation__ = "{0}.setAutoCalibration({1})"

    def send_command(self, command: int) -> None:
        """
        Send a custom command to the sensor.

        Args:
            command (int): Command byte.

        """
        __use_as_is__ = False
        __translation__ = "{0}.sendCommand({1})"
