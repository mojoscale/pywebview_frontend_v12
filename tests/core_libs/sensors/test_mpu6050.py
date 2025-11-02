# tests/mpu6050_test.py
import sensors.mpu6050 as sensor_mpu


def setup() -> None:
    sensor = sensor_mpu.MPU6050Sensor()

    # Initialize sensor with standard gyro/accel config
    sensor.begin(3, 3)

    # Perform basic operations
    sensor.update()
    sensor.read_acceleration()
    sensor.read_gyro()
    sensor.read_angles()
    sensor.get_temperature()

    # Calibration methods
    sensor.set_gyro_offsets(0.1, -0.1, 0.05)
    sensor.set_acc_offsets(0.02, -0.03, 0.04)
    sensor.calc_offsets()

    # Address operations

    sensor.get_angle_x()
    sensor.get_angle_y()
    sensor.get_angle_z()

    sensor.set_filter_gyro_coef(1.11)
    sensor.set_filter_acc_coef(1.11)
    sensor.get_filter_gyro_coef()
    sensor.get_filter_acc_coef()
    sensor.fetch_data()

    print("MPU6050 basic compile test successful.")


def loop() -> None:
    pass
