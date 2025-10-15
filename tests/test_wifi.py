import wifi as w
import arduino as a


wi_fi_client = w.WiFiClient()


def setup() -> None:
    while w.wifi_is_connected() == False:
        w.wifi_connect("user", "pass", 180)
        w.wifi_begin("user", "pass")

    print(f"wifi connected and ip is {w.wifi_localIP()}")

    available_networks = w.scan_network()
    for network in available_networks:
        print(f"network: {network}")


def loop() -> None:
    pass
