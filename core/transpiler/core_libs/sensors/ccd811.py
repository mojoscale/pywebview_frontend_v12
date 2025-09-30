__include_modules__ = "Adafruit_CCS811"
__include_internal_modules__ = ""
__dependencies__ = ""


class CCS811Sensor:
    def __init__(self):
        """
        Initialize the CCS811 sensor. Use begin() after this to start communication.
        """
        __use_as_is__ = False
        __class_actual_type__ = "Adafruit_CCS811"
        __translation__ = ""

    def begin(self) -> bool:
        """
        Start the sensor with default I2C address.
        """
        __use_as_is__ = False
        __translation__ = "{0}.begin()"

    def available(self) -> bool:
        """
        Check if new data is available.
        """
        __use_as_is__ = False
        __translation__ = "{0}.available()"

    def read_data(self) -> bool:
        """
        Read latest sensor data.
        """
        __use_as_is__ = False
        __translation__ = "{0}.readData()"

    def get_eco2(self) -> int:
        """
        Return eCO2 in ppm.
        """
        __use_as_is__ = False
        __translation__ = "{0}.geteCO2()"

    def get_tvoc(self) -> int:
        """
        Return TVOC in ppb.
        """
        __use_as_is__ = False
        __translation__ = "{0}.getTVOC()"

    def set_environmental_data(self, humidity: float, temperature: float) -> None:
        """
        Provide humidity (%) and temperature (°C) for compensation.
        """
        __use_as_is__ = False
        __translation__ = "{0}.setEnvironmentalData({1}, {2})"

    def get_error_id(self) -> int:
        """
        Get the error ID from the sensor.
        """
        __use_as_is__ = False
        __translation__ = "{0}.getErrorID()"
