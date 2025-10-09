import sensors.mq2 as sensor_mq2


def setup() -> None:
    sensor = sensor_mq2.MQ2Sensor(0)

    # Start the sensor
    sensor.begin()

    # Read all values
    sensor.read(False)

    # Individual gases
    sensor.read_lpg()
    sensor.read_co()
    sensor.read_smoke()

    print("MQ2 compile test successful.")


def loop() -> None:
    pass
