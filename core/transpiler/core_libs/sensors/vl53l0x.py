__include_modules__ = "Adafruit_VL53L0X"
__dependencies__ = "adafruit/Adafruit_VL53L0X"
__include_internal_modules__ = "helpers/sensors/VL53L0XHelper"


class VL53L0XSensor:
    def __init__(self):
        """
        VL53L0X time-of-flight distance sensor.
        Uses I2C (default address: 0x29).
        """
        __use_as_is__ = False
        __class_actual_type__ = "Adafruit_VL53L0X"
        __translation__ = ""

    def begin(self, i2c_addr: int, debug: bool) -> bool:
        """
        Initialize the sensor.

        Args:
            i2c_addr (int): I2C address (default 0x29).
            debug (bool): Enable debug logging.

        Returns:
            bool: True if initialization succeeded.
        """
        __translation__ = "{0}.begin({1}, {2})"

    def set_address(self, new_addr: int) -> bool:
        """
        Set a new I2C address for the sensor.

        Args:
            new_addr (int): New address to assign.

        Returns:
            bool: True if successful.
        """
        __translation__ = "{0}.setAddress({1})"

    def read_range(self) -> int:
        """
        Perform a single range read.

        Returns:
            int: Distance in millimeters.
        """
        __translation__ = "{0}.readRange()"

    def read_range_status(self) -> int:
        """
        Get status of the last range reading.

        Returns:
            int: Status code (0 = OK).
        """
        __translation__ = "{0}.readRangeStatus()"

    def start_range(self) -> bool:
        """
        Start a range measurement.

        Returns:
            bool: True if started.
        """
        __translation__ = "{0}.startRange()"

    def is_range_complete(self) -> bool:
        """
        Check if the range measurement is complete.

        Returns:
            bool: True if complete.
        """
        __translation__ = "{0}.isRangeComplete()"

    def wait_range_complete(self) -> bool:
        """
        Wait for the range to complete.

        Returns:
            bool: True if completed.
        """
        __translation__ = "{0}.waitRangeComplete()"

    def read_range_result(self) -> int:
        """
        Read the result of the last range.

        Returns:
            int: Distance in millimeters.
        """
        __translation__ = "{0}.readRangeResult()"

    def start_range_continuous(self, period_ms: int) -> bool:
        """
        Start continuous ranging mode.

        Args:
            period_ms (int): Delay between measurements. Default 50.

        Returns:
            bool: True if successful.
        """
        __translation__ = "{0}.startRangeContinuous({1})"

    def stop_range_continuous(self) -> None:
        """
        Stop continuous ranging mode.
        """
        __translation__ = "{0}.stopRangeContinuous()"

    def timeout_occurred(self) -> bool:
        """
        Check if timeout occurred.

        Returns:
            bool: True if timeout occurred.
        """
        __translation__ = "{0}.timeoutOccurred()"

    def config_sensor(self, mode: int) -> bool:
        """
        Configure predefined sensor mode.

        Args:
            mode (int): One of:
                - 0 = default
                - 1 = long range
                - 2 = high speed
                - 3 = high accuracy

        Returns:
            bool: True if configuration successful.
        """
        __translation__ = "custom_vl53l0x_helper_config_sensor({0}, {1})"

    def set_measurement_timing_budget(self, budget_us: int) -> bool:
        """
        Set measurement timing budget in microseconds.

        Args:
            budget_us (int): Time budget in µs.

        Returns:
            bool: True if set.
        """
        __translation__ = "{0}.setMeasurementTimingBudgetMicroSeconds({1})"

    def get_measurement_timing_budget(self) -> int:
        """
        Get measurement timing budget.

        Returns:
            int: Time budget in µs.
        """
        __translation__ = "{0}.getMeasurementTimingBudgetMicroSeconds()"

    def set_vcsel_pulse_period(self, period_type: int, pulse_period: int) -> bool:
        """
        Set VCSEL pulse period.

        Args:
            period_type (int): VCSEL period enum.
            pulse_period (int): Pulse width in units.

        Returns:
            bool: True if set.
        """
        __translation__ = "{0}.setVcselPulsePeriod({1}, {2})"

    def get_vcsel_pulse_period(self, period_type: int) -> int:
        """
        Get VCSEL pulse period.

        Args:
            period_type (int): VCSEL period enum.

        Returns:
            int: Pulse period value.
        """
        __translation__ = "{0}.getVcselPulsePeriod({1})"
