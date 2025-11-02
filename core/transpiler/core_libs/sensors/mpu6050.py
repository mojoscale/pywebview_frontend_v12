__include_modules__ = "MPU6050_light,Wire"
__include_internal_modules__ = "helpers/sensors/MPU6050Helper"
__dependencies__ = "rfetick/MPU6050_light@^1.1.0"


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
        __translation__ = "{self}.begin({gyro_config_num}, {acc_config_num})"
        return 0

    def update(self) -> None:
        """
        Reads all new data from the sensor.
        Call before using any `get*()` method.
        """
        __use_as_is__ = False
        __translation__ = "{self}.update()"

    def read_acceleration(self) -> list[float]:
        """
        Returns current acceleration readings in g (gravity units).

        Returns:
            list[float]: [accX, accY, accZ] in g
        """
        __use_as_is__ = False
        __translation__ = "custom_mpu6050_helper_read_acceleration({self})"

        return []

    def read_gyro(self) -> list[float]:
        """
        Returns current gyroscope angular velocity in degrees/sec.

        Returns:
            list[float]: [gyroX, gyroY, gyroZ] in °/s
        """
        __use_as_is__ = False
        __translation__ = "custom_mpu6050_helper_read_gyro({self})"

        return []

    def read_angles(self) -> list[float]:
        """
        Returns estimated orientation angles using a complementary filter.

        Returns:
            list[float]: [angleX, angleY, angleZ] in degrees
        """
        __use_as_is__ = False
        __translation__ = "custom_mpu6050_helper_read_acceleration({self})"
        return []

    def get_angle_x(self) -> float:
        """
        Returns orientation angle along x-axis
        """
        __translation__ = "{self}.getAngleX()"

    def get_angle_y(self) -> float:
        """
        Returns orientation angle along y-axis
        """
        __translation__ = "{self}.getAngleY()"

    def get_angle_z(self) -> float:
        """
        Returns orientation angle along z-axis
        """
        __translation__ = "{self}.getAngleZ()"

    def get_temperature(self) -> float:
        """
        Returns:
            float: Temperature in °C
        """
        __use_as_is__ = False
        __translation__ = "{self}.getTemp()"
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
        __translation__ = "{self}.setGyroOffsets({x}, {y}, {z})"

    def set_acc_offsets(self, x: float, y: float, z: float) -> None:
        """
        Manually calibrate accelerometer offsets.

        Args:
            x (float): X-axis offset in g
            y (float): Y-axis offset in g
            z (float): Z-axis offset in g
        """
        __use_as_is__ = False
        __translation__ = "{self}.setAccOffsets({x}, {y}, {z})"

    def calc_offsets(self, calc_gyro: bool = True, calc_acc: bool = True) -> None:
        """
        Automatically calculate gyro and/or accelerometer offsets.
        Sensor must be stable during this process.

        Args:
            calc_gyro (bool): Calibrate gyroscope
            calc_acc (bool): Calibrate accelerometer
        """
        __use_as_is__ = False
        __translation__ = "{self}.calcOffsets({calc_gyro}, {calc_acc})"

    def set_filter_gyro_coef(self, coef: float) -> None:
        """
        Adjust the complementary filter’s gyro weighting coefficient.

        Args:
            coef (float): Gyroscope weighting (0.0–1.0).
                Higher values emphasize gyro data; lower values favor accelerometer data.
        """
        __use_as_is__ = False
        __translation__ = "{self}.setFilterGyroCoef({coef})"

    def set_filter_acc_coef(self, coef: float) -> None:
        """
        Adjust the complementary filter’s accelerometer weighting coefficient.

        Args:
            coef (float): Accelerometer weighting (0.0–1.0).
                Typically, acc_coef = 1.0 - gyro_coef.
        """
        __use_as_is__ = False
        __translation__ = "{self}.setFilterAccCoef({coef})"

    def get_filter_gyro_coef(self) -> float:
        """
        Retrieve the current complementary filter gyroscope coefficient.

        Returns:
            float: Current gyro weighting (0.0–1.0).
        """
        __use_as_is__ = False
        __translation__ = "{self}.getFilterGyroCoef()"
        return 0.98

    def get_filter_acc_coef(self) -> float:
        """
        Retrieve the current complementary filter accelerometer coefficient.

        Returns:
            float: Current accelerometer weighting (0.0–1.0).
        """
        __use_as_is__ = False
        __translation__ = "{self}.getFilterAccCoef()"
        return 0.02

    def fetch_data(self) -> None:
        """
        Perform a low-level data fetch directly from sensor registers.
        Normally, use `update()` instead of this.
        """
        __use_as_is__ = False
        __translation__ = "{self}.fetchData()"
