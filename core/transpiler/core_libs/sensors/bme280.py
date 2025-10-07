__dependencies__ = (
    "adafruit/Adafruit BME280 Library@^2.2.2,adafruit/Adafruit Unified Sensor@^1.1.9"
)

__include_modules__ = "Adafruit_Sensor,Adafruit_BME280"
__include_internal_modules__ = ""


class BME280Sensor:
    def __init__(self) -> None:
        """
        Initializes the BME280 sensor. Requires `begin()` to be called later.
        """
        __use_as_is__ = False
        __class_actual_type__ = "Adafruit_BME280"
        __translation__ = ""  # Translates to global object
        pass

    def begin(self, address: int) -> bool:
        """
        Initializes communication with the BME280 sensor.

        Args:
            address (int): I2C address of the sensor (usually 0x76 or 0x77).

        Returns:
            bool: True if sensor initialized correctly, False otherwise.
        """
        __use_as_is__ = False
        __translation__ = "{0}.begin({1})"
        return False

    def read_temperature(self) -> float:
        """
        Reads temperature in Celsius.

        Returns:
            float: Temperature in °C.
        """
        __use_as_is__ = False
        __translation__ = "{0}.readTemperature()"
        return 0.0

    def read_humidity(self) -> float:
        """
        Reads relative humidity in %.

        Returns:
            float: Humidity percentage.
        """
        __use_as_is__ = False
        __translation__ = "{0}.readHumidity()"
        return 0.0

    def read_pressure(self) -> float:
        """
        Reads pressure in Pascals.

        Returns:
            float: Atmospheric pressure in Pa.
        """
        __use_as_is__ = False
        __translation__ = "{0}.readPressure()"
        return 0.0

    def read_altitude(self, sea_level_hpa: float) -> float:
        """
        Calculates altitude based on current pressure and known sea level pressure.

        Args:
            sea_level_hpa (float): Known sea level pressure in hPa.

        Returns:
            float: Estimated altitude in meters.
        """
        __use_as_is__ = False
        __translation__ = "{0}.readAltitude({1})"
        return 0.0
