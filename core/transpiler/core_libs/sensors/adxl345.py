"""
ADXL345 Accelerometer Module
============================

This module provides a Python-style abstraction for the **Adafruit ADXL345** 3-axis accelerometer, 
allowing you to easily configure range, data rate, and read acceleration data in a Pythonic way.  
It wraps the `Adafruit_ADXL345_U` and `Adafruit_Sensor` C++ libraries, enabling usage from 
transpiled Python code with full compatibility on ESP32/ESP8266 and other Arduino boards.

**Features**
- 3-axis acceleration measurement (X, Y, Z)
- Configurable range: ±2g, ±4g, ±8g, ±16g
- Adjustable data output rate
- Access to raw register-level operations
- Device ID and configuration helpers
- I2C communication (default address: 0x53)

**Dependencies**
- Adafruit ADXL345 (`adafruit/Adafruit ADXL345`)
- Adafruit Unified Sensor (`Adafruit_Sensor`)
- Internal helper: `helpers/sensors/ADXL345Helper`

**Sample Code**
```python
import sensors.adxl345 as sensor_adxl

adxl = sensor_adxl.ADXL345Sensor(0x53)

def setup() -> None:
    adxl.begin(0x53)
    adxl.set_range(2)        # ±8g
    adxl.set_data_rate(10)   # Medium speed

def loop() -> None:
    accel = adxl.read_acceleration()
    print(f"Acceleration: X={accel[0]}, Y={accel[1]}, Z={accel[2]}")
```
"""


__include_modules__ = "Adafruit_ADXL345_U,Adafruit_Sensor"
__include_internal_modules__ = "helpers/sensors/ADXL345Helper"
__dependencies__ = "adafruit/Adafruit ADXL345"


class ADXL345Sensor:
    """
    ADXL345 accelerometer sensor stub using the Adafruit_ADXL345 library.

    This class supports 3-axis acceleration sensing with configurable range and data rate.

    I2C default address: 0x53
    """

    def __init__(self, id: int) -> None:
        """
        Create an instance of the ADXL345 sensor.

        Args:
            id (int): Identifier for the sensor. Just pick
                     a unique integer.
        """
        __use_as_is__ = False
        __class_actual_type__ = "Adafruit_ADXL345_Unified"
        __construct_with_equal_to__ = True
        __translation__ = "Adafruit_ADXL345_Unified({id})"

    def begin(self, address: int = 0x53) -> bool:
        """
        Initializes the sensor.

        Args:
            address (int): I2C address (default is 0x53)

        Returns:
            bool: True if successful, False if not
        """
        __use_as_is__ = False
        __translation__ = "{self}.begin({address})"
        return True

    def set_range(self, range_val: int = 0) -> None:
        """
        Set the ADXL345 sensor's measurement range.

        The measurement range determines the maximum acceleration (in g) that
        the sensor can detect on each axis. Larger ranges allow detection of
        stronger motion but reduce resolution.

        Args:
            range_val (int): Range selector value from 0–3, corresponding to:
                0 → ±2g
                1 → ±4g
                2 → ±8g
                3 → ±16g

        Example:
            ```python
            adxl.set_range(2)  # sets range to ±8g
            ```

        Notes:
            - Defaults to ±2g if the value is invalid.
            - Internally maps to the Adafruit `range_t` enum.
        """
        __use_as_is__ = False
        __translation__ = "setADXLRange({self},{range_val})"

    def get_range(self) -> str:
        """
        Get current measurement range.

        Returns:
            int: Current range value
        """
        __use_as_is__ = False
        __translation__ = "getADXLRangeText({self})"
        return 0

    def set_data_rate(self, rate: int = 10) -> None:
        """
        Set the ADXL345 sensor's data output rate.

        The data rate determines how frequently acceleration data is updated and made
        available for reading. Higher rates improve responsiveness but increase power
        consumption.

        Args:
            rate (int): Data rate selector value from 0–15, corresponding to:
                0 → 0.10 Hz
                1 → 0.20 Hz
                2 → 0.39 Hz
                3 → 0.78 Hz
                4 → 1.56 Hz
                5 → 3.13 Hz
                6 → 6.25 Hz
                7 → 12.5 Hz
                8 → 25 Hz
                9 → 50 Hz
                10 → 100 Hz
                11 → 200 Hz
                12 → 400 Hz
                13 → 800 Hz
                14 → 1600 Hz
                15 → 3200 Hz

        Example:
            ```python
            adxl.set_data_rate(10)  # sets update rate to 100 Hz
            ```

        Notes:
            - Defaults to 100 Hz if the rate value is invalid.
            - Internally maps to the Adafruit `dataRate_t` enum.
        """
        __use_as_is__ = False
        __translation__ = "setADXLDataRate({self}, {rate})"

    def get_data_rate(self) -> str:
        """
        Get current data output rate.

        Returns:
            int: Data rate value
        """
        __use_as_is__ = False
        __translation__ = "getADXLDataRateText({self})"
        return 0

    def read_acceleration(self) -> list[float]:
        """
        Reads current acceleration on all three axes.

        Returns:
            list[float]: [x, y, z] in g
        """
        __use_as_is__ = False
        __translation__ = "custom_adxl345_helper_read_acceleration(&{self})"

    def get_device_id(self) -> int:
        """
        Read the device ID (should be 0xE5).

        Returns:
            int: Device ID
        """
        __use_as_is__ = False
        __translation__ = "{self}.getDeviceID()"
        return 0xE5

    def write_register(self, reg: int, value: int) -> None:
        """
        Write value to specified register.

        Args:
            reg (int): Register address
            value (int): Value to write
        """
        __use_as_is__ = False
        __translation__ = "{self}.writeRegister({reg}, {value})"

    def read_register(self, reg: int) -> int:
        """
        Read value from specified register.

        Args:
            reg (int): Register address

        Returns:
            int: Register value
        """
        __use_as_is__ = False
        __translation__ = "{self}.readRegister({reg})"
        return 0

    def read16(self, reg: int) -> int:
        """
        Read 16-bit value from specified register.

        Args:
            reg (int): Register address

        Returns:
            int: 16-bit value
        """
        __use_as_is__ = False
        __translation__ = "{self}.read16({reg})"
        return 0

    def get_x(self) -> int:
        """
        Returns raw acceleration in X-axis.

        Returns:
            int: Raw X value
        """
        __use_as_is__ = False
        __translation__ = "{self}.getX()"
        return 0

    def get_y(self) -> int:
        """
        Returns raw acceleration in Y-axis.

        Returns:
            int: Raw Y value
        """
        __use_as_is__ = False
        __translation__ = "{self}.getY()"
        return 0

    def get_z(self) -> int:
        """
        Returns raw acceleration in Z-axis.

        Returns:
            int: Raw Z value
        """
        __use_as_is__ = False
        __translation__ = "{self}.getZ()"
        return 0
