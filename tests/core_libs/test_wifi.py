import comms.wifi as w
import core.arduino as a


wi_fi_client = w.WiFiClient()


def setup() -> None:
    while w.wifi_is_connected() == False:
        w.wifi_begin("user", "pass")

    print(f"wifi connected and ip is {w.wifi_localIP()}")

    available_networks = w.scan_network()
    for network in available_networks:
        print(f"network: {network}")

    did_connect = wi_fi_client.connect("host", 80)
    written = wi_fi_client.write("data")
    wi_fi_client.print("data")
    wi_fi_client.println("data")

    is_available = wi_fi_client.available()
    bytes_read = wi_fi_client.read()
    number_bytes_read = wi_fi_client.read_bytes("buffer", 10)
    readstring = wi_fi_client.read_string()
    next_byte = wi_fi_client.peek()
    wi_fi_client.flush()
    wi_fi_client.stop()

    is_connected = wi_fi_client.connected()


def loop() -> None:
    pass
