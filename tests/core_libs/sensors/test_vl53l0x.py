import sensors.vl53l0x as vl


def setup() -> None:
    sensor = vl.VL53L0XSensor()

    sensor.begin(0x29, False)
    sensor.set_address(0x30)
    sensor.read_range()
    sensor.read_range_status()
    sensor.start_range()
    sensor.is_range_complete()
    sensor.wait_range_complete()
    sensor.read_range_result()
    sensor.start_range_continuous(50)
    sensor.stop_range_continuous()
    sensor.timeout_occurred()
    sensor.config_sensor(1)
    sensor.set_measurement_timing_budget(20000)
    sensor.get_measurement_timing_budget()
    sensor.set_vcsel_pulse_period(0, 8)
    sensor.get_vcsel_pulse_period(0)


def loop() -> None:
    pass
