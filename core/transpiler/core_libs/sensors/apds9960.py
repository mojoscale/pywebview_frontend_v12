__include_modules__ = "Adafruit_APDS9960"
__dependencies__ = "adafruit/Adafruit APDS9960 Library @ ^1.1.4"
__include_internal_modules__ = "helpers/sensors/APDS9960Helper"


class APDS9960Sensor:
    def __init__(self):
        """
        Create an instance of the APDS9960 sensor.
        Provides access to color, proximity, and gesture sensing.
        """
        __use_as_is__ = False
        __class_actual_type__ = "Adafruit_APDS9960"
        __translation__ = ""

    def begin(self, iTimeMS: int, gain: int, address: int) -> bool:
        """
        Initialize the APDS9960 sensor.

        Args:
            iTimeMS (int): Integration time in milliseconds. Typical range is 10–700 ms.
            gain (int): Analog gain value:
                - 0 → 1x gain
                - 1 → 4x gain
                - 2 → 16x gain
                - 3 → 64x gain
            address (int): I2C address of the sensor (default is 0x39).

        Returns:
            bool: True if initialization succeeded, False otherwise.

        Translation:
            custom_apds9960_helper_begin(sensor_instance, iTimeMS, gain, address)
        """
        __translation__ = "custom_apds9960_helper_begin({0}, {1}, {2}, {3})"

    def set_adc_integration_time(self, time_ms: int) -> None:
        """
        Set color sensing integration time.

        Args:
            time_ms (int): Integration time in milliseconds.
        """
        __translation__ = "{0}.setADCIntegrationTime({1})"

    def get_adc_integration_time(self) -> float:
        """
        Get the currently set integration time for color sensing.

        Returns:
            float: Integration time in milliseconds.
        """
        __translation__ = "{0}.getADCIntegrationTime()"

    def set_adc_gain(self, gain: int) -> None:
        """
        Set gain for the ADC during color measurement.

        Args:
            gain (int): Gain value (0=1x, 1=4x, 2=16x, 3=64x).
        """
        __translation__ = "{0}.setADCGain({1})"

    def get_adc_gain(self) -> int:
        """
        Get the currently set ADC gain.

        Returns:
            int: Gain value.
        """
        __translation__ = "{0}.getADCGain()"

    def set_led(self, drive: int, boost: int) -> None:
        """
        Set LED drive strength and boost.

        Args:
            drive (int): Drive strength (e.g., 0–3).
            boost (int): LED boost percentage (e.g., 0=100%, 1=150%, 2=200%, 3=300%).
        """
        __translation__ = "{0}.setLED({1}, {2})"

    def enable_proximity(self, enable: bool = True) -> None:
        """
        Enable or disable the proximity sensor.

        Args:
            enable (bool): Set to True to enable.
        """
        __translation__ = "{0}.enableProximity({1})"

    def set_prox_gain(self, gain: int) -> None:
        """
        Set proximity sensor gain.

        Args:
            gain (int): Gain (0=1x, 1=2x, 2=4x, 3=8x).
        """
        __translation__ = "{0}.setProxGain({1})"

    def get_prox_gain(self) -> int:
        """
        Get current proximity gain setting.

        Returns:
            int: Proximity gain.
        """
        __translation__ = "{0}.getProxGain()"

    def set_prox_pulse(self, pulse_len: int, pulses: int) -> None:
        """
        Set length and count of proximity pulses.

        Args:
            pulse_len (int): Pulse length (e.g., 0=4µs ... 3=32µs).
            pulses (int): Number of pulses.
        """
        __translation__ = "{0}.setProxPulse({1}, {2})"

    def enable_proximity_interrupt(self) -> None:
        """Enable interrupt when proximity crosses threshold."""
        __translation__ = "{0}.enableProximityInterrupt()"

    def disable_proximity_interrupt(self) -> None:
        """Disable proximity threshold interrupt."""
        __translation__ = "{0}.disableProximityInterrupt()"

    def read_proximity(self) -> int:
        """
        Read proximity value from sensor.

        Returns:
            int: Raw proximity measurement.
        """
        __translation__ = "{0}.readProximity()"

    def set_proximity_interrupt_threshold(
        self, low: int, high: int, persistence: int = 4
    ) -> None:
        """
        Set thresholds and persistence for proximity interrupts.

        Args:
            low (int): Minimum threshold.
            high (int): Maximum threshold.
            persistence (int): How many consecutive crossings to trigger interrupt.
        """
        __translation__ = "{0}.setProximityInterruptThreshold({1}, {2}, {3})"

    def get_proximity_interrupt(self) -> bool:
        """
        Check if a proximity interrupt was triggered.

        Returns:
            bool: True if triggered.
        """
        __translation__ = "{0}.getProximityInterrupt()"

    def enable_gesture(self, enable: bool = True) -> None:
        """
        Enable gesture detection.

        Args:
            enable (bool): True to enable gesture sensing.
        """
        __translation__ = "{0}.enableGesture({1})"

    def gesture_valid(self) -> bool:
        """
        Check if a gesture event is available to read.

        Returns:
            bool: True if a gesture is available.
        """
        __translation__ = "{0}.gestureValid()"

    def set_gesture_dimensions(self, dims: int) -> None:
        """
        Set dimensions used for gesture detection (e.g., up/down, left/right).

        Args:
            dims (int): Bitmask of axes to use.
        """
        __translation__ = "{0}.setGestureDimensions({1})"

    def set_gesture_fifo_threshold(self, threshold: int) -> None:
        """
        Set FIFO level threshold for gesture recognition.

        Args:
            threshold (int): Threshold level.
        """
        __translation__ = "{0}.setGestureFIFOThreshold({1})"

    def set_gesture_gain(self, gain: int) -> None:
        """
        Set gesture detection gain.

        Args:
            gain (int): Gain level.
        """
        __translation__ = "{0}.setGestureGain({1})"

    def set_gesture_proximity_threshold(self, threshold: int) -> None:
        """
        Set gesture proximity threshold to start detecting gestures.

        Args:
            threshold (int): Proximity threshold.
        """
        __translation__ = "{0}.setGestureProximityThreshold({1})"

    def set_gesture_offset(self, up: int, down: int, left: int, right: int) -> None:
        """
        Set directional offset compensation for gesture detection.

        Args:
            up (int): Up offset.
            down (int): Down offset.
            left (int): Left offset.
            right (int): Right offset.
        """
        __translation__ = "{0}.setGestureOffset({1}, {2}, {3}, {4})"

    def read_gesture(self) -> int:
        """
        Read detected gesture code.

        Returns:
            int: Gesture code (e.g., up, down, left, right).
        """
        __translation__ = "{0}.readGesture()"

    def reset_counts(self) -> None:
        """
        Reset gesture detection internal counters.
        """
        __translation__ = "{0}.resetCounts()"

    def enable_color(self, enable: bool = True) -> None:
        """
        Enable color sensing features.

        Args:
            enable (bool): True to enable.
        """
        __translation__ = "{0}.enableColor({1})"

    def color_data_ready(self) -> bool:
        """
        Check if color data is ready to read.

        Returns:
            bool: True if data is ready.
        """
        __translation__ = "{0}.colorDataReady()"

    def get_color_data(self) -> list[int]:
        """
        Read raw color channel values.

        Returns:
            list[int]: [r, g, b, c] (red, green, blue, clear).
        """
        __translation__ = "custom_apds9960_helper_get_color_data({0})"

    def calculate_color_temperature(self, r: int, g: int, b: int) -> int:
        """
        Calculate color temperature from RGB values.

        Args:
            r (int): Red.
            g (int): Green.
            b (int): Blue.

        Returns:
            int: Color temperature in Kelvin.
        """
        __translation__ = "{0}.calculateColorTemperature({1}, {2}, {3})"

    def calculate_lux(self, r: int, g: int, b: int) -> int:
        """
        Calculate lux from RGB values.

        Args:
            r (int): Red.
            g (int): Green.
            b (int): Blue.

        Returns:
            int: Lux value.
        """
        __translation__ = "{0}.calculateLux({1}, {2}, {3})"

    def enable_color_interrupt(self) -> None:
        """Enable interrupt on color thresholds."""
        __translation__ = "{0}.enableColorInterrupt()"

    def disable_color_interrupt(self) -> None:
        """Disable color interrupt."""
        __translation__ = "{0}.disableColorInterrupt()"

    def clear_interrupt(self) -> None:
        """Clear all interrupt flags."""
        __translation__ = "{0}.clearInterrupt()"

    def set_int_limits(self, low: int, high: int) -> None:
        """
        Set lower and upper limits for interrupt triggering.

        Args:
            low (int): Lower threshold.
            high (int): Upper threshold.
        """
        __translation__ = "{0}.setIntLimits({1}, {2})"

    def enable(self, enable: bool = True) -> None:
        """
        Master enable or disable for the sensor.

        Args:
            enable (bool): True to turn on all functions.
        """
        __translation__ = "{0}.enable({1})"
