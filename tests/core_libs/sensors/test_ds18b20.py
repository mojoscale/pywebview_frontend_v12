import sensors.ds18b20 as sensor_ds18b20
import onewire as ow


def setup() -> None:
    # Create mock OneWire instance (placeholder object)
    onewire = ow.OneWire(2)

    # Initialize DS18B20 sensor with the OneWire instance
    sensor = sensor_ds18b20.DS18B20Sensor(onewire)

    # Begin communication
    sensor.begin()

    # Request temperature and read it
    sensor.request_temperature()
    sensor.read_temperature(0)

    print("DS18B20 basic compile test successful.")


def loop() -> None:
    pass
