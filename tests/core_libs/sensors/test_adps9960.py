import sensors.apds9960 as sensor_apds


def setup() -> None:
    apds = sensor_apds.APDS9960Sensor()

    # Initialization
    apds.begin(100, 1, 0x39)
    apds.enable(True)

    # ADC / Color settings
    apds.set_adc_integration_time(100)
    apds.get_adc_integration_time()
    apds.set_adc_gain(2)
    apds.get_adc_gain()

    # LED / Proximity configuration
    apds.set_led(1, 2)
    apds.enable_proximity(True)
    apds.set_prox_gain(2)
    apds.get_prox_gain()
    apds.set_prox_pulse(2, 8)
    apds.set_proximity_interrupt_threshold(10, 200, 2)
    apds.enable_proximity_interrupt()
    apds.disable_proximity_interrupt()
    apds.read_proximity()
    apds.get_proximity_interrupt()

    # Gesture configuration
    apds.enable_gesture(True)
    apds.set_gesture_dimensions(0)
    apds.set_gesture_fifo_threshold(2)
    apds.set_gesture_gain(1)
    apds.set_gesture_proximity_threshold(50)
    apds.set_gesture_offset(10, 10, 9, 12)
    apds.gesture_valid()
    apds.read_gesture()
    apds.reset_counts()

    # Color sensing
    apds.enable_color(True)
    apds.color_data_ready()
    apds.get_color_data()
    apds.calculate_color_temperature(120, 100, 80)
    apds.calculate_lux(120, 100, 80)
    apds.enable_color_interrupt()
    apds.disable_color_interrupt()

    # Interrupts and thresholds
    apds.clear_interrupt()
    apds.set_int_limits(100, 1000)

    # Wrap up
    apds.enable(False)

    print("APDS9960 basic test compile successful.")


def loop() -> None:
    # Nothing here — only setup testing compilation
    pass
