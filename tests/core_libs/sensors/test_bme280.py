import sensors.bme280 as sensor_bme280


def setup() -> None:
    sensor = sensor_bme280.BME280Sensor()

    sensor.begin()
    sensor.read_temperature()
    sensor.read_humidity()
    sensor.read_pressure()
    sensor.read_altitude(1013.25)

    print("BME280 basic compile test successful.")


def loop() -> None:
    pass
