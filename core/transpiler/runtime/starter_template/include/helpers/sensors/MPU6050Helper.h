#include "MPU6050_light.h"
#include "PyList.h"

PyList<float> custom_mpu6050_helper_read_acceleration(MPU6050& sensor) {
    float x = sensor.getAccX();
    float y = sensor.getAccY();
    float z = sensor.getAccZ();
    return PyList<float>::from({x, y, z});
}

PyList<float> custom_mpu6050_helper_read_gyro(MPU6050& sensor) {
    float x = sensor.getGyroX();
    float y = sensor.getGyroY();
    float z = sensor.getGyroZ();
    return PyList<float>::from({x, y, z});
}

PyList<float> custom_mpu6050_helper_read_angles(MPU6050& sensor) {
    float x = sensor.getAngleX();
    float y = sensor.getAngleY();
    float z = sensor.getAngleZ();
    return PyList<float>::from({x, y, z});
}