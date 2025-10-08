"""
DHT Sensor Module
=================

This module provides a Python-style abstraction layer for **DHT11** and **DHT22** sensors,
allowing seamless integration within the transpiler environment. It wraps the underlying
C++ `DHT` class and its helper (`DHTHelper`), enabling temperature and humidity readings
using clean, intuitive Python syntax.

The transpiler automatically converts these calls to equivalent Arduino C++ code,
linking with the `adafruit/DHT sensor library`.

**Dependencies:**
    - adafruit/DHT sensor library

**Includes:**
    - DHT (hardware driver)
    - helpers/sensors/DHTHelper (internal helper for combined reads)

Example:
```python
import sensors.dht as sensor_dht

dht = sensor_dht.DHTSensor(2, "DHT11")

def setup() -> None:
    dht.begin()

def loop() -> None:
    temp = dht.read_temperature(False)
    humidity = dht.read_humidity()
    print(f"Temperature is {temp}")
    print(f"Humidity is {humidity}")
```
"""


__include_modules__ = "DHT"
__include_internal_modules__ = "helpers/sensors/DHTHelper"
__dependencies__ = "adafruit/DHT sensor library"


class DHTSensor:
    """
    A Python-like abstraction for DHT11 and DHT22 sensors.
    """

    def __init__(self, pin: int, type: str) -> None:
        """
        Initialize the DHT sensor on a specific GPIO pin.

        Args:
            pin (int): GPIO pin connected to the sensor.
            type (str): Type of the sensor: "DHT11" or "DHT22".
        """
        __use_as_is__ = False
        __class_actual_type__ = "DHT"
        __construct_with_equal_to__ = True
        __translation__ = "createDHTSensor({1}, {2})"

    def begin(self) -> None:
        """
        Begin communication with the sensor.
        """
        __use_as_is__ = True
        pass

    def read_temperature(self, is_fahrenheit: bool) -> float:
        """
        Read the temperature.

        Args:
            is_fahrenheit (bool): Whether to read in Fahrenheit.

        Returns:
            float: Temperature value.
        """
        __use_as_is__ = False
        __translation__ = "{0}.readTemperature()"
        return 0.0

    def read_humidity(self) -> float:
        """
        Read the humidity percentage.

        Returns:
            float: Humidity value.
        """
        __use_as_is__ = False
        __translation__ = "{0}.readHumidity()"
        return 0.0

    def read(self) -> dict[str, float]:
        """
        Read both temperature and humidity.

        Returns:
            dict: {"temperature": float, "humidity": float}
        """
        __use_as_is__ = False
        __translation__ = "custom_dht_helper_read({0})"
        return {"temperature": 0.0, "humidity": 0.0}
