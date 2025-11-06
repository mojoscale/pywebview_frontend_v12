import comms.wifi as w
import comms.mqtt as m
import core.arduino as ad

wi_fi_client = w.WiFiClient()

psc = m.PubSubClient(wi_fi_client)


def callback(topic: str, payload: str) -> None:
    print(f"received {payload} on {topic}")


def setup() -> None:
    w.wifi_begin("ssid", "pass")
    while not w.wifi_is_connected():
        ad.delay(1000)
        print("connection.....")

    psc.set_server("broker.hivemq.com")
    psc.set_callback(callback)
    psc.connect("client_id", username="user", password="password")

    psc.publish("topic", "message", retained=True)

    psc.subscribe("some_topic", qos=1)

    psc.unsubscribe("topic")

    is_connected = psc.connected()

    print(f"is mqtt connected: {is_connected}")

    psc.set_keep_alive(10)
    psc.setSocketTimeout(10)
    psc.set_buffer_size(10)

    psc.disconnect()


def loop() -> None:
    pass
