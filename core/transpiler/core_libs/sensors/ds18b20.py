__include_modules__ = "OneWire,DallasTemperature"
__include_internal_modules__ = "helpers/sensors/DS18B20Helper"
__dependencies__ = "milesburton/DallasTemperature,PaulStoffregen/OneWire"


class DS18B20Sensor:
    """
    A Python-like abstraction for DS18B20 temperature sensors using OneWire protocol.
    """

    def __init__(self, onewire_pin: int) -> None:
        """
        Initialize the DS18B20 sensor on a specific GPIO pin.

        Args:
            pin (int): GPIO pin connected to the OneWire data line.
        """
        __use_as_is__ = False
        __class_actual_type__ = "DallasTemperature"
        __construct_with_equal_to__ = True
        __pass_as__ = "pointer"
        __translation__ = "create_dallas_sensor({onewire_pin})"

    def begin(self) -> None:
        """
        Begin communication with the DS18B20 sensor.
        """
        __use_as_is__ = True
        __translation__ = "{self}->begin()"
        pass

    def request_temperature(self) -> None:
        """
        Request temperature reading from the sensor. Must be called before read.
        """
        __use_as_is__ = False
        __translation__ = "{self}->requestTemperatures()"
        pass

    def read_temperature(self, index: int = 1) -> float:
        """
        Read the temperature in Celsius from a specific sensor (index-based).

        Args:
            index (int): Sensor index (useful if multiple sensors on the same bus).

        Returns:
            float: Temperature in Celsius.
        """
        __use_as_is__ = False
        __translation__ = "{self}->getTempCByIndex({index})"
        return 0.0
