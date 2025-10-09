__include_modules__ = "Adafruit_CCS811,Adafruit_I2CDevice"
__include_internal_modules__ = ""
__dependencies__ = "adafruit/Adafruit BusIO"


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
        Initialize the CCS811 sensor over I2C.

        Returns:
            bool: True if sensor initialized successfully.
        """
        __use_as_is__ = False
        __translation__ = "{0}.begin()"

    def available(self) -> bool:
        """
        Check whether new measurement data is available.

        Returns:
            bool: True if new data is available.
        """
        __use_as_is__ = False
        __translation__ = "{0}.available()"

    def read_data(self) -> bool:
        """
        Read the latest data sample from the sensor.

        Returns:
            bool: True if the read succeeded.
        """
        __use_as_is__ = False
        __translation__ = "{0}.readData()"

    def get_eco2(self) -> int:
        """
        Get the equivalent CO2 (eCO2) reading in parts per million (ppm).

        Returns:
            int: eCO2 concentration in ppm.
        """
        __use_as_is__ = False
        __translation__ = "{0}.geteCO2()"

    def get_tvoc(self) -> int:
        """
        Get the Total Volatile Organic Compounds (TVOC) reading in parts per billion (ppb).

        Returns:
            int: TVOC concentration in ppb.
        """
        __use_as_is__ = False
        __translation__ = "{0}.getTVOC()"

    def set_environmental_data(self, humidity: float, temperature: float) -> None:
        """
        Provide humidity (%) and temperature (°C) data for compensation.

        Args:
            humidity (float): Relative humidity percentage.
            temperature (float): Ambient temperature in °C.
        """
        __use_as_is__ = False
        __translation__ = "{0}.setEnvironmentalData({1}, {2})"

    def calculate_temperature(self) -> float:
        """
        Calculate temperature using the onboard thermistor.

        Returns:
            float: Temperature in Celsius.
        """
        __use_as_is__ = False
        __translation__ = "{0}.calculateTemperature()"

    def set_drive_mode(self, mode: int) -> None:
        """
        Set the sensor’s drive mode.

        Args:
            mode (int): Drive mode (0–4). Each mode defines a different measurement frequency.
        """
        __use_as_is__ = False
        __translation__ = "{0}.setDriveMode({1})"
