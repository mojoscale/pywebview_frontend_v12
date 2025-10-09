# ------------------------------------------------------------
import sensors.tsl2561 as tsl


def setup() -> None:
    print("=== TSL2561 Sensor Test Start ===")

    # Create sensor instance at default address 0x39
    sensor = tsl.TSL2561Sensor(0x39)

    # --- Initialization ---
    print("Initializing sensor...")
    success = sensor.begin()
    print("Begin status:", success)

    # --- Auto Range ---
    print("Enabling auto range...")
    sensor.enable_auto_range(True)
    print("Disabling auto range...")
    sensor.enable_auto_range(False)
    print("Re-enabling auto range...")
    sensor.enable_auto_range(True)

    # --- Gain and Integration Time ---
    print("Setting gain (0 = 1x, 1 = 16x)...")
    sensor.set_gain(1)
    print("Setting integration time (0=13ms, 1=101ms, 2=402ms)...")
    sensor.set_integration_time(2)

    # --- Read Raw Luminosity ---
    print("Reading broadband and IR values...")
    values = sensor.get_luminosity()
    broadband = values[0]
    ir = values[1]
    print("Broadband:", broadband, "IR:", ir)

    # --- Calculate Lux ---
    print("Calculating Lux from broadband and IR values...")
    lux = sensor.calculate_lux(broadband, ir)
    print("Calculated Lux:", lux)

    print("=== TSL2561 Sensor Test Complete ===")


def loop() -> None:
    # Optional: Continuous readings can be added here
    pass
