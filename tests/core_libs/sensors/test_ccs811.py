import sensors.ccs811 as sensor_ccs


def setup() -> None:
    sensor = sensor_ccs.CCS811Sensor()

    sensor.begin()
    sensor.available()
    sensor.read_data()
    sensor.get_eco2()
    sensor.get_tvoc()
    sensor.set_environmental_data(45.0, 25.0)
    sensor.calculate_temperature()
    sensor.set_drive_mode(1)

    print("CCS811 basic compile test successful.")


def loop() -> None:
    pass
