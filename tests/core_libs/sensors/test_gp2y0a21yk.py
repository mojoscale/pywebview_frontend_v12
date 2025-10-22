import sensors.gp2y0a21yk as sensor_gp


def setup() -> None:
    sensor = sensor_gp.GP2Y0A21YKSensor(10)
    dist = sensor.distance()

    print(f"distance is {dist}")


def loop() -> None:
    pass
