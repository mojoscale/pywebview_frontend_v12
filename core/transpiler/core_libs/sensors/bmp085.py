__include_modules__ = "Adafruit_BMP085_U,Wire,Adafruit_Sensor"
__include_internal_modules__ = "helpers/sensors/BMP085Helper"
__dependencies__ = "adafruit/Adafruit BMP085 Unified"


class BMP085Sensor:
    """
    BMP085 pressure and temperature sensor stub using the Adafruit_BMP085_Unified library.
    """

    def __init__(self) -> None:
        """
        Create an instance of the BMP085 sensor.
        """
        __use_as_is__ = False
        __class_actual_type__ = "Adafruit_BMP085_Unified"
        __construct_with_equal_to__ = True
        __translation__ = "Adafruit_BMP085_Unified()"

    def begin(self, mode: int = 3) -> bool:
        """
        Initialize the sensor with a specific mode.

        Args:
            mode (int): Operating mode:
                - 0 = ULTRALOWPOWER
                - 1 = STANDARD
                - 2 = HIGHRES
                - 3 = ULTRAHIGHRES (default)

        Returns:
            bool: True if initialized successfully
        """
        __use_as_is__ = False
        __translation__ = "custom_bmp085_helper_begin(&{self}, {mode})"
        return True

    def get_temperature(self) -> float:
        """
        Reads temperature from the sensor.

        Returns:
            float: Temperature in Celsius
        """
        __use_as_is__ = False
        __translation__ = "custom_bmp085_helper_get_temperature(&{self})"
        return 0.0

    def get_pressure(self) -> float:
        """
        Reads pressure from the sensor.

        Returns:
            float: Pressure in Pa
        """
        __use_as_is__ = False
        __translation__ = "custom_bmp085_helper_get_pressure(&{self})"
        return 0.0

    def pressure_to_altitude(self, sea_level: float, atmospheric: float) -> float:
        """
        Converts pressure to altitude.

        Args:
            sea_level (float): Sea level pressure
            atmospheric (float): Measured pressure

        Returns:
            float: Altitude in meters
        """
        __use_as_is__ = False
        __translation__ = "{self}.pressureToAltitude({sea_level}, {atmospheric})"
        return 0.0

    def pressure_to_altitude_with_temp(
        self, sea_level: float, atmospheric: float, temp: float
    ) -> float:
        """
        Converts pressure to altitude with temperature adjustment.

        Args:
            sea_level (float): Sea level pressure
            atmospheric (float): Measured pressure
            temp (float): Measured temperature

        Returns:
            float: Altitude in meters
        """
        __use_as_is__ = False
        __translation__ = (
            "{self}.pressureToAltitude({sea_level}, {atmospheric}, {temp})"
        )
        return 0.0

    def sea_level_for_altitude(self, altitude: float, atmospheric: float) -> float:
        """
        Calculates pressure at sea level from altitude.

        Args:
            altitude (float): Altitude in meters
            atmospheric (float): Measured pressure

        Returns:
            float: Sea level pressure
        """
        __use_as_is__ = False
        __translation__ = "{self}.seaLevelForAltitude({altitude}, {atmospheric})"
        return 0.0

    def sea_level_for_altitude_with_temp(
        self, altitude: float, atmospheric: float, temp: float
    ) -> float:
        """
        Calculates sea level pressure with temperature adjustment.

        Args:
            altitude (float): Altitude in meters
            atmospheric (float): Measured pressure
            temp (float): Temperature

        Returns:
            float: Sea level pressure
        """
        __use_as_is__ = False
        __translation__ = (
            "{self}.seaLevelForAltitude({altitude}, {atmospheric}, {temp})"
        )
        return 0.0

    def get_event(self) -> dict[str, float]:
        """
        Reads a unified sensor event.

        Returns:
            dict: {'pressure': float, 'temperature': float}
        """
        __use_as_is__ = False
        __translation__ = "custom_bmp085_helper_get_event(&{self})"
        return {"pressure": 0.0, "temperature": 0.0}

    def get_sensor_info(self) -> dict[str, str]:
        """
        Gets sensor metadata.

        Returns:
            dict: Metadata dictionary
        """
        __use_as_is__ = False
        __translation__ = "custom_bmp085_helper_get_sensor_info(&{self})"
        return {"name": "BMP085", "type": "pressure"}
