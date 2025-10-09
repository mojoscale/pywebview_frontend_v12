import sensors.dht as sensor_dht


def setup() -> None:
    dht = sensor_dht.DHTSensor(4, "DHT22")

    dht.begin()
    dht.read_temperature(False)
    dht.read_humidity()
    dht.read()

    print("✅ DHT basic compile test successful.")


def loop() -> None:
    pass
