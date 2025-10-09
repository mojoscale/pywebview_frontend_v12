__include_modules__ = "OneWire,DallasTemperature"
__include_internal_modules__ = ""
__dependencies__ = "milesburton/DallasTemperature"


class DS18B20Sensor:
    """
    A Python-like abstraction for DS18B20 temperature sensors using OneWire protocol.
    """

    def __init__(self, onewire_instance: OneWire) -> None:
        """
        Initialize the DS18B20 sensor on a specific GPIO pin.

        Args:
            pin (int): GPIO pin connected to the OneWire data line.
        """
        __use_as_is__ = False
        __class_actual_type__ = "DallasTemperature"
        __translation__ = "(&{1})"

    def begin(self) -> None:
        """
        Begin communication with the DS18B20 sensor.
        """
        __use_as_is__ = True
        pass

    def request_temperature(self) -> None:
        """
        Request temperature reading from the sensor. Must be called before read.
        """
        __use_as_is__ = False
        __translation__ = "{0}.requestTemperatures()"
        pass

    def read_temperature(self, index: int) -> float:
        """
        Read the temperature in Celsius from a specific sensor (index-based).

        Args:
            index (int): Sensor index (useful if multiple sensors on the same bus).

        Returns:
            float: Temperature in Celsius.
        """
        __use_as_is__ = False
        __translation__ = "{0}.getTempCByIndex({1})"
        return 0.0
