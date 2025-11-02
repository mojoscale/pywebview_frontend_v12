import sensors.bh1750 as sensor_bh1750


def setup() -> None:
    sensor = sensor_bh1750.BH1750Sensor(0x23)

    sensor.begin()
    sensor.configure(2)
    sensor.set_mtreg(69)
    sensor.measurement_ready(True)
    sensor.read_light_level()

    print("✅ BH1750 basic compile test successful.")


def loop() -> None:
    pass
