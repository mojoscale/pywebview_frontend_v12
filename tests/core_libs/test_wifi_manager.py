import wifi_manager as wm


def setup() -> None:
    wifi_manager = wm.WiFiManager()

    wifi_manager.set_debug_output(True)
    wifi_manager.reset_settings()
    result1 = wifi_manager.auto_connect("MyAP", "mypassword")
    result2 = wifi_manager.start_config_portal("ConfigAP", "configpass")
    wifi_manager.set_timeout(180)
    wifi_manager.set_connect_timeout(60)
    wifi_manager.set_minimum_signal_quality(70)


def loop() -> None:
    pass
