import sensors.adxl345 as sensor_adxl


def setup() -> None:
    adxl = sensor_adxl.ADXL345Sensor(1)

    adxl.begin(0x53)
    adxl.set_range(2)
    adxl.get_range()
    adxl.set_data_rate(10)
    adxl.get_data_rate()
    adxl.read_acceleration()
    adxl.get_device_id()
    adxl.write_register(0x2D, 0x08)
    adxl.read_register(0x00)
    adxl.read16(0x32)
    adxl.get_x()
    adxl.get_y()
    adxl.get_z()

    print("ADXL345 basic compile test successful.")


def loop() -> None:
    pass
