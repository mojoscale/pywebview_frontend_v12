# --- test_sgp30.py (transpiled to Arduino-compatible test) ---

import sensors.sgp30 as spg


def setup() -> None:
    sensor = spg.SGP30Sensor()

    print("Initializing SGP30...")
    success = sensor.begin()
    print("Begin:", success)

    connected = sensor.is_connected()
    print("Connected:", connected)

    # Read basic info
    sensor.generic_reset()
    sensor.get_id()
    feature = sensor.get_feature_set()
    print("Feature set:", feature)

    # Perform a self-test
    test_ok = sensor.measure_test()
    print("Measure test:", test_ok)

    # Make a normal measurement
    measured = sensor.measure(True)
    print("Measure:", measured)

    # Fetch readings
    tvoc = sensor.get_tvoc()
    co2 = sensor.get_co2()
    print("TVOC:", tvoc, "CO2:", co2)

    # Optional raw values
    sensor.request_raw()
    sensor.read_raw()
    print("H2_raw:", sensor.get_h2_raw(), "Ethanol_raw:", sensor.get_ethanol_raw())

    # Advanced info
    error_code = sensor.last_error()
    print("Last error:", error_code)


def loop() -> None:
    pass
