__include_modules__ = "NewPing"
__dependencies__ = ""  # Adjust version to your PlatformIO setup


class UltrasonicSensor:
    def __init__(self, trigger_pin: int, echo_pin: int, max_cm_distance: int):
        """
        Represents an ultrasonic distance sensor using the NewPing library.

        This class supports low-level ultrasonic sensors that work via
        digital pulse duration, specifically those with a trigger pin and
        echo pin.

        ✅ Supported sensor models:
        - HC-SR04
        - SRF05
        - DYP-ME007
        - Parallax PING)))™ (single-pin supported)
        - SRF06 (with capacitor or dual-pin mode only)

        ❌ Not supported:
        - Analog sensors (e.g., Sharp GP2Y series)
        - I2C/SPI ToF sensors (e.g., VL53L0X, VL6180X)

        Args:
            trigger_pin (int): GPIO pin used to send trigger pulse.
            echo_pin (int): GPIO pin used to receive echo pulse.
            max_cm_distance (int, optional): Maximum measurable distance in cm. Default is 500.
        """
        __use_as_is__ = False
        __class_actual_type__ = "NewPing"
        __translation__ = "({1}, {2})"

    def ping(self) -> int:
        """
        Send a ping and return the echo time in microseconds.

        Returns:
            int: Echo duration in microseconds.
        """
        __translation__ = "{0}.ping()"

    def ping_in(self) -> int:
        """
        Send a ping and return the distance in whole inches.

        Returns:
            int: Distance in inches.
        """
        __translation__ = "{0}.ping_in()"

    def ping_cm(self) -> int:
        """
        Send a ping and return the distance in whole centimeters.

        Returns:
            int: Distance in centimeters.
        """
        __translation__ = "{0}.ping_cm()"

    def ping_median(self, iterations: int) -> int:
        """
        Perform multiple pings and return the median echo time (in microseconds).
        Helps filter out invalid readings.

        Args:
            iterations (int): Number of pings to average. Default is 5.

        Returns:
            int: Median echo time in microseconds.
        """
        __translation__ = "{0}.ping_median({1})"

    def convert_in(self, echo_time: int) -> int:
        """
        Convert echo time to distance in inches.

        Args:
            echo_time (int): Echo duration in microseconds.

        Returns:
            int: Distance in inches.
        """
        __translation__ = "{0}.convert_in({1})"

    def convert_cm(self, echo_time: int) -> int:
        """
        Convert echo time to distance in centimeters.

        Args:
            echo_time (int): Echo duration in microseconds.

        Returns:
            int: Distance in centimeters.
        """
        __translation__ = "{0}.convert_cm({1})"
