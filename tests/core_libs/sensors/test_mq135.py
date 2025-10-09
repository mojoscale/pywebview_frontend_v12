import sensors.mq135 as mq


def setup() -> None:
    sensor = mq.MQ135Sensor(0)  # Analog pin A0 → 0

    # Basic readings
    sensor.get_correction_factor(25.0, 50.0)
    sensor.get_resistance()
    sensor.get_corrected_resistance(25.0, 50.0)
    sensor.get_ppm()
    sensor.get_corrected_ppm(25.0, 50.0)
    sensor.get_rzero()
    sensor.get_corrected_rzero(25.0, 50.0)

    print("MQ135 basic compile test successful.")


def loop() -> None:
    pass
