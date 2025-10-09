import sensors.sht31 as sht


def setup() -> None:
    sensor = sht.SHT31Sensor(0x44)

    print("Initializing SHT31...")
    ok = sensor.begin(0x44)
    print("Begin:", ok)

    temp = sensor.read_temperature()
    hum = sensor.read_humidity()
    print("Temperature:", temp, "C", "Humidity:", hum, "%")

    # Reset sensor
    sensor.reset()

    # Heater control test
    print("Heater initially:", sensor.heater_enabled())
    sensor.toggle_heater(True)
    print("Heater on:", sensor.heater_enabled())
    sensor.toggle_heater(False)
    print("Heater off:", sensor.heater_enabled())


def loop() -> None:
    pass
