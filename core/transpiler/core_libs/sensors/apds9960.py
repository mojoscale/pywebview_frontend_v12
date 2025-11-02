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

    def begin(self, iTimeMS: int = 10, gain: int = 1, address: int = 0x39) -> bool:
        """
        Initialize the APDS9960 sensor.

        Args:
            iTimeMS (int): Integration time in milliseconds. Typical range is 10–700 ms.
                  Default 10 ms.
            gain (int): Analog gain value:
                - 0 → 1x gain
                - 1 → 4x gain
                - 2 → 16x gain
                - 3 → 64x gain
                default 1(4x)
            address (int): I2C address of the sensor (default is 0x39).

        Returns:
            bool: True if initialization succeeded, False otherwise.

        Translation:
            custom_apds9960_helper_begin(sensor_instance, iTimeMS, gain, address)
        """
        __translation__ = (
            "custom_apds9960_helper_begin({self}, {iTimeMS}, {gain}, {address})"
        )

    def set_adc_integration_time(self, time_ms: int) -> None:
        """
        Set color sensing integration time.

        Args:
            time_ms (int): Integration time in milliseconds.
        """
        __translation__ = "{self}.setADCIntegrationTime({time_ms})"

    def get_adc_integration_time(self) -> int:
        """
        Get the currently set integration time for color sensing.

        Returns:
            float: Integration time in milliseconds.
        """
        __translation__ = "{self}.getADCIntegrationTime()"

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
        __translation__ = "setAPDS9960ADCGain({self}, {gain})"

    def get_adc_gain(self) -> int:
        """
        Get the currently set ADC gain.

        Returns:
            int: Gain value.
        """
        __translation__ = "{self}.getADCGain()"

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
        __translation__ = "configureAPDS9960LED({self}, {drive}, {boost})"

    def enable_proximity(self, enable: bool = True) -> None:
        """
        Enable or disable the proximity sensor.

        Args:
            enable (bool): Set to True to enable.
        """
        __translation__ = "{self}.enableProximity({enable})"

    def set_prox_gain(self, gain: int) -> None:
        """
        Set proximity sensor gain.

        Args:
            gain (int): Gain (0=1x, 1=2x, 2=4x, 3=8x).
        """
        __translation__ = "configureAPDS9960ProxGain({self}, {gain})"

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
        __translation__ = "{self}.getProxGain()"

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
        __translation__ = "configureAPDS9960ProxPulse({self}, {pulse_len}, {pulses})"

    def enable_proximity_interrupt(self) -> None:
        """Enable interrupt when proximity crosses threshold."""
        __translation__ = "{self}.enableProximityInterrupt()"

    def disable_proximity_interrupt(self) -> None:
        """Disable proximity threshold interrupt."""
        __translation__ = "{self}.disableProximityInterrupt()"

    def read_proximity(self) -> int:
        """
        Read proximity value from sensor.

        Returns:
            int: Raw proximity measurement.
        """
        __translation__ = "{self}.readProximity()"

    def set_proximity_interrupt_threshold(
        self, low: int, high: int, persistence: int = 4
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
                generating an interrupt. Default 4.

        Returns:
            None

        Notes:
            Use this to avoid false triggers from transient movements
            by setting appropriate threshold limits and persistence
            for stable proximity event detection.
        """
        __translation__ = (
            "{self}.setProximityInterruptThreshold({low}, {high}, {persistence})"
        )

    def get_proximity_interrupt(self) -> bool:
        """
        Check if a proximity interrupt was triggered.

        Returns:
            bool: True if triggered.
        """
        __translation__ = "{self}.getProximityInterrupt()"

    def enable_gesture(self, enable: bool = True) -> None:
        """
        Enable gesture detection.

        Args:
            enable (bool): True to enable gesture sensing.
        """
        __translation__ = "{self}.enableGesture({enable})"

    def gesture_valid(self) -> bool:
        """
        Check if a gesture event is available to read.

        Returns:
            bool: True if a gesture is available.
        """
        __translation__ = "{self}.gestureValid()"

    def set_gesture_dimensions(self, dims: int) -> None:
        """
        Set dimensions used for gesture detection (e.g., up/down, left/right).

        Args:
            dims (int): Bitmask of axes to use.
        """
        __translation__ = "{self}.setGestureDimensions({dims})"

    def set_gesture_fifo_threshold(self, threshold: int) -> None:
        """
        Set FIFO level threshold for gesture recognition.

        Args:
            threshold (int): Threshold level.
        """
        __translation__ = "{self}.setGestureFIFOThreshold({threshold})"

    def set_gesture_gain(self, gain: int) -> None:
        """
        Set gesture detection gain.

        Args:
            gain (int): Gain level.
        """
        __translation__ = "{self}.setGestureGain({gain})"

    def set_gesture_proximity_threshold(self, threshold: int) -> None:
        """
        Set gesture proximity threshold to start detecting gestures.

        Args:
            threshold (int): Proximity threshold.
        """
        __translation__ = "{self}.setGestureProximityThreshold({threshold})"

    def set_gesture_offset(self, up: int, down: int, left: int, right: int) -> None:
        """
        Set directional offset compensation for gesture detection.

        Args:
            up (int): Up offset.
            down (int): Down offset.
            left (int): Left offset.
            right (int): Right offset.
        """
        __translation__ = "{self}.setGestureOffset({up}, {down}, {left}, {right})"

    def read_gesture(self) -> int:
        """
        Read detected gesture code.

        Returns:
            int: Gesture code (e.g., up, down, left, right).
        """
        __translation__ = "{self}.readGesture()"

    def reset_counts(self) -> None:
        """
        Reset gesture detection internal counters.
        """
        __translation__ = "{self}.resetCounts()"

    def enable_color(self, enable: bool = True) -> None:
        """
        Enable color sensing features.

        Args:
            enable (bool): True to enable.
        """
        __translation__ = "{self}.enableColor({enable})"

    def color_data_ready(self) -> bool:
        """
        Check if color data is ready to read.

        Returns:
            bool: True if data is ready.
        """
        __translation__ = "{self}.colorDataReady()"

    def get_color_data(self) -> list[int]:
        """
        Read raw color channel values.

        Returns:
            list[int]: [r, g, b, c] (red, green, blue, clear).
        """
        __translation__ = "custom_apds9960_helper_get_color_data({self})"

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
        __translation__ = "{self}.calculateColorTemperature({g}, {g}, {b})"

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
        __translation__ = "{self}.calculateLux({r}, {g}, {b})"

    def enable_color_interrupt(self) -> None:
        """Enable interrupt on color thresholds."""
        __translation__ = "{self}.enableColorInterrupt()"

    def disable_color_interrupt(self) -> None:
        """Disable color interrupt."""
        __translation__ = "{self}.disableColorInterrupt()"

    def clear_interrupt(self) -> None:
        """Clear all interrupt flags."""
        __translation__ = "{self}.clearInterrupt()"

    def set_int_limits(self, low: int, high: int) -> None:
        """
        Set lower and upper limits for interrupt triggering.

        Args:
            low (int): Lower threshold.
            high (int): Upper threshold.
        """
        __translation__ = "{self}.setIntLimits({low}, {high})"

    def enable(self, enable: bool = True) -> None:
        """
        Master enable or disable for the sensor.

        Args:
            enable (bool): True to turn on all functions.
        """
        __translation__ = "{self}.enable({enable})"
