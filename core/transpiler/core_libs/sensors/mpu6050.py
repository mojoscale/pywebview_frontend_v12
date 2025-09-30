__include_modules__ = "MPU6050_light,Wire"
__include_internal_modules__ = "helpers/sensors/MPU6050Helper"
__dependencies__ = "rfetick/MPU6050_light"


class MPU6050Sensor:
    """
    MPU6050 Light Sensor stub using the rfetick/MPU6050_light library.

    This class supports basic 6-axis motion sensing:
    - Accelerometer (±2G to ±16G)
    - Gyroscope (±250°/s to ±2000°/s)
    - Optional temperature readout
    - Complementary filter for angle estimation

    Default I2C address is 0x68.
    Set to 0x69 if AD0 pin is pulled high.
    """

    def __init__(self) -> None:
        """
        Create an instance of the MPU6050 sensor with default I2C address (0x68).
        Call `begin()` before reading data.
        """
        __use_as_is__ = False
        __class_actual_type__ = "MPU6050"
        __translation__ = "(Wire)"

    def begin(self, gyro_config_num: int, acc_config_num: int) -> int:
        """
        Initialize the sensor.

        Args:
            gyro_config_num (int): 0=±250, 1=±500, 2=±1000, 3=±2000 deg/s
            acc_config_num (int):  0=±2G, 1=±4G, 2=±8G, 3=±16G

        Returns:
            int: 0 on success, 1 on failure
        """
        __use_as_is__ = False
        __translation__ = "{0}.begin({1}, {2})"
        return 0

    def update(self) -> None:
        """
        Reads all new data from the sensor.
        Call before using any `get*()` method.
        """
        __use_as_is__ = False
        __translation__ = "{0}.update()"

    def read_acceleration(self) -> list[float]:
        """
        Returns current acceleration readings in g (gravity units).

        Returns:
            list[float]: [accX, accY, accZ] in g
        """
        __use_as_is__ = False
        __translation__ = "custom_mpu6050_helper_read_acceleration({0})"

        return []

    def read_gyro(self) -> list[float]:
        """
        Returns current gyroscope angular velocity in degrees/sec.

        Returns:
            list[float]: [gyroX, gyroY, gyroZ] in °/s
        """
        __use_as_is__ = False
        __translation__ = "custom_mpu6050_helper_read_gyro({0})"

        return []

    def read_angles(self) -> list[float]:
        """
        Returns estimated orientation angles using a complementary filter.

        Returns:
            list[float]: [angleX, angleY, angleZ] in degrees
        """
        __use_as_is__ = False
        __translation__ = "custom_mpu6050_helper_read_acceleration({0})"
        return []

    def read_temperature(self) -> float:
        """
        Returns:
            float: Temperature in °C
        """
        __use_as_is__ = False
        __translation__ = "{0}.readTemp()"
        return 0.0

    def set_gyro_offsets(self, x: float, y: float, z: float) -> None:
        """
        Manually calibrate gyroscope offsets.

        Args:
            x (float): X-axis offset in °/s
            y (float): Y-axis offset in °/s
            z (float): Z-axis offset in °/s
        """
        __use_as_is__ = False
        __translation__ = "{0}.setGyroOffsets({1}, {2}, {3})"

    def set_acc_offsets(self, x: float, y: float, z: float) -> None:
        """
        Manually calibrate accelerometer offsets.

        Args:
            x (float): X-axis offset in g
            y (float): Y-axis offset in g
            z (float): Z-axis offset in g
        """
        __use_as_is__ = False
        __translation__ = "{0}.setAccOffsets({1}, {2}, {3})"

    def calc_offsets(self, calc_gyro: bool, calc_acc: bool) -> None:
        """
        Automatically calculate gyro and/or accelerometer offsets.
        Sensor must be stable during this process.

        Args:
            calc_gyro (bool): Calibrate gyroscope
            calc_acc (bool): Calibrate accelerometer
        """
        __use_as_is__ = False
        __translation__ = "{0}.calcOffsets({1}, {2})"

    def set_address(self, addr: int) -> None:
        """
        Change I2C address for the sensor (0x68 or 0x69).

        Args:
            addr (int): New I2C address
        """
        __use_as_is__ = False
        __translation__ = "{0}.setAddress({1})"

    def get_address(self) -> int:
        """
        Returns:
            int: Current I2C address (typically 0x68 or 0x69)
        """
        __use_as_is__ = False
        __translation__ = "{0}.getAddress()"
        return 0x68
