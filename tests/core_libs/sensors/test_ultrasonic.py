import sensors.ultrasonic as u


def setup() -> None:
    sensor = u.UltrasonicSensor(5, 18, 200)
    sensor.ping()
    sensor.ping_in()
    sensor.ping_cm()
    sensor.ping_median(5)
    sensor.convert_in(1000)
    sensor.convert_cm(1000)


def loop() -> None:
    pass
