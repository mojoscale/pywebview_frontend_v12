import wifi as w
import mqtt as m

wi_fi_client = w.WiFiClient()

psc = m.PubSubClient(wi_fi_client)


def callback(topic: str, payload: str) -> None:
    print(f"received {payload} on {topic}")


def setup() -> None:
    while not w.wifi_is_connected():
        w.wifi_connect("ssid", "password", 180)

    psc.set_server("mqtt.mojoscale.com", 1883)
    psc.set_callback(callback)
    psc.connect_simple("client_id")
    psc.connect_with_auth("client_id", "user", "passworsubscribe_with_qosd")
    psc.connect_with_last_will("client_id", "topic", 1, True, "message")
    psc.connect_full("client_id", "user", "pass", "topic", 1, False, "message")
    psc.publish_simple("topic", "message")
    psc.publish_retained("topic", "payload", False)
    psc.subscribe("some_topic")
    psc.subscribe_with_qos("topic", 1)
    psc.unsubscribe("topic")

    is_connected = psc.connected()

    psc.set_keep_alive(10)
    psc.setSocketTimeout(10)
    psc.set_buffer_size(10)
    psc.set_clean_session(True)

    psc.disconnect()


def loop() -> None:
    pass
