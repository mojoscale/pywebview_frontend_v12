import sensors.mhz19 as sensor_mhz19
import hardware_serial as hs


def setup() -> None:
    # Simulate hardware serial (in Arduino this would be Serial1, Serial2, etc.)
    stream = hs.HardwareSerial(2)

    sensor = sensor_mhz19.MHZ19Sensor(17, 16, baud=115200)

    # Initialize / retrieve data

    # Read sensor values
    sensor.get_co2()

    sensor.get_temperature()
    sensor.get_accuracy()

    # Configuration and calibration calls
    sensor.set_range(5000)
    sensor.calibrate_zero()
    sensor.auto_calibration(True)
    sensor.auto_calibration()

    print("MHZ19 basic compile test successful.")


def loop() -> None:
    pass
