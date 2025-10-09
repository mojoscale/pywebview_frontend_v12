import sensors.bmp085 as sensor_bmp


def setup() -> None:
    sensor = sensor_bmp.BMP085Sensor()

    sensor.begin(3)
    sensor.get_temperature()
    sensor.get_pressure()
    sensor.pressure_to_altitude(1013.25, 900.0)
    sensor.pressure_to_altitude_with_temp(1013.25, 900.0, 25.0)
    sensor.sea_level_for_altitude(150.0, 900.0)
    sensor.sea_level_for_altitude_with_temp(150.0, 900.0, 25.0)
    sensor.get_event()
    sensor.get_sensor_info()

    print("BMP085 basic compile test successful.")


def loop() -> None:
    pass
