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

    def get_adc_integration_time(self) -> int:
        """
        Get the currently set integration time for color sensing.

        Returns:
            float: Integration time in milliseconds.
        """
        __translation__ = "{0}.getADCIntegrationTime()"

    def set_adc_gain(self, gain: int) -> None:
        """
        Set the APDS9960 sensor's ADC (Analog-to-Digital Converter) gain.

        The ADC gain determines the sensitivity of the color sensing channel.
        Higher gains allow the sensor to detect faint light, while lower gains
        prevent saturation in bright environments.

        Args:
            gain (int): Gain selector value from 0–3, corresponding to:
                0 → 1×  (lowest sensitivity)
                1 → 4×
                2 → 16×
                3 → 64× (highest sensitivity)

        Example:
            ```python
            apds.set_adc_gain(2)  # sets ADC gain to 16×
            ```

        Notes:
            - Defaults to 1× if an invalid value is provided.
            - Internally maps to the Adafruit `apds9960AGain_t` enum.
        """
        __translation__ = "setAPDS9960ADCGain({0}, {1})"

    def get_adc_gain(self) -> int:
        """
        Get the currently set ADC gain.

        Returns:
            int: Gain value.
        """
        __translation__ = "{0}.getADCGain()"

    def set_led(self, drive: int, boost: int) -> None:
        """
        Configures the infrared (IR) emitter LED drive and boost settings
        for the APDS9960 sensor.

        This method adjusts the current and boost factor that control
        the intensity of the IR LED used for proximity and gesture
        detection. Higher drive or boost values increase LED brightness
        and sensing range but also raise power consumption.

        Args:
            drive (int): LED drive current code (0–3).
                Maps to approximate current levels as follows:
                    0 → 100 mA
                    1 → 50 mA
                    2 → 25 mA
                    3 → 12.5 mA

            boost (int): LED current boost multiplier code (0–3).
                Maps to effective current scaling factors:
                    0 → 100%
                    1 → 150%
                    2 → 200%
                    3 → 300%

        Returns:
            None

        """
        __translation__ = "configureAPDS9960LED({0}, {1}, {2})"

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
        __translation__ = "configureAPDS9960ProxGain({0}, {1})"

    def get_prox_gain(self) -> int:
        """
        Retrieves the currently configured proximity gain level.

        Returns:
            int: The proximity gain multiplier as a user-friendly integer
            (1, 2, 4, or 8), representing the effective sensitivity applied
            to the proximity sensing engine.

        Notes:
            This value is returned in a human-readable form rather than a
            raw register code, allowing users to work directly with familiar
            gain factors used in proximity configuration.
        """
        __translation__ = "{0}.getProxGain()"

    def set_prox_pulse(self, pulse_len: int, pulses: int) -> None:
        """
        Configures the proximity sensing pulse sequence.

        This sets both the duration of each IR LED pulse and the total
        number of pulses emitted during each proximity measurement cycle.
        Longer or more frequent pulses increase detection range but also
        raise power consumption.

        Args:
            pulse_len (int): Pulse duration code (0–3), mapped to
                user-friendly time intervals:
                    0 → 4 µs
                    1 → 8 µs
                    2 → 16 µs
                    3 → 32 µs

            pulses (int): Number of IR LED pulses per proximity cycle
                (range: 0–63). Higher values improve sensitivity at the
                cost of additional measurement time.

        Returns:
            None

        Notes:
            This method provides an intuitive interface for tuning the
            proximity sensor’s performance by combining pulse width and
            count into a single configuration call.
        """
        __translation__ = "configureAPDS9960ProxPulse({0}, {1}, {2})"

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
        self, low: int, high: int, persistence: int
    ) -> None:
        """
        Configures the proximity interrupt trigger conditions.

        This sets the low and high threshold values that determine
        when the proximity interrupt fires, along with a persistence
        value that controls how many consecutive readings must exceed
        those thresholds before triggering.

        Args:
            low (int): Lower threshold (0–255). The interrupt will trigger
                when proximity values fall below this limit.
            high (int): Upper threshold (0–255). The interrupt will trigger
                when proximity values exceed this limit.
            persistence (int): Number of consecutive readings (0–15)
                required to confirm the threshold condition before
                generating an interrupt.

        Returns:
            None

        Notes:
            Use this to avoid false triggers from transient movements
            by setting appropriate threshold limits and persistence
            for stable proximity event detection.
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
