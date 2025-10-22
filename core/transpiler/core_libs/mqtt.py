__include_modules__ = "PubSubClient"
__include_internal_modules__ = "helpers/MQTTHelper"
__dependencies__ = "knolleary/PubSubClient"


class PubSubClient:
    """
    A lightweight MQTT client for Arduino (ESP32/ESP8266) supporting publish/subscribe.
    """

    def __init__(self, wifi_client: WiFiClient) -> None:
        """
        Initialize with a WiFiClient instance.

        Args:
            wifi_client: A WiFiClient instance (TCP transport layer)
        """
        __use_as_is__ = False
        __class_actual_type__ = "PubSubClient"
        __translation__ = "({1})"
        pass

    def set_server(self, host: str, port: int) -> None:
        """
        Set the MQTT broker address and port.
        """
        __use_as_is__ = False
        __translation__ = "{0}.setServer({1}.c_str(), {2})"
        pass

    def set_callback(self, callback_func: callable) -> None:
        """
        Set the callback function for received MQTT messages.
        """
        __use_as_is__ = False
        __translation__ = "setupSimpleCallback({0}, {1})"
        pass

    def connect_simple(self, client_id: str) -> bool:
        """
        Connect to the MQTT broker with just a client ID.
        """
        __use_as_is__ = False
        __translation__ = "{0}.connect({1}.c_str())"
        return False

    def connect_with_auth(self, client_id: str, username: str, password: str) -> bool:
        """
        Connect to the MQTT broker with authentication.
        """
        __use_as_is__ = False
        __translation__ = "{0}.connect({1}.c_str(), {2}.c_str(), {3}.c_str())"
        return False

    def connect_with_last_will(
        self,
        client_id: str,
        will_topic: str,
        will_qos: int,
        will_retain: bool,
        will_message: str,
    ) -> bool:
        """
        Connect with a last will message, no authentication.
        """
        __use_as_is__ = False
        __translation__ = "{0}.connect({1}.c_str(), {2}.c_str(), {3}, {4}, {5}.c_str())"
        return False

    def connect_full(
        self,
        client_id: str,
        username: str,
        password: str,
        will_topic: str,
        will_qos: int,
        will_retain: bool,
        will_message: str,
    ) -> bool:
        """
        Connect with auth and last will message.
        """
        __use_as_is__ = False
        __translation__ = "{0}.connect({1}.c_str(), {2}.c_str(), {3}.c_str(), {4}.c_str(), {5}, {6}, {7}.c_str())"
        return False

    def publish_simple(self, topic: str, payload: str) -> bool:
        """
        Publish a plain string payload to a topic.
        """
        __use_as_is__ = False
        __translation__ = "{0}.publish({1}.c_str(), {2}.c_str())"
        return False

    def publish_retained(self, topic: str, payload: str, retained: bool) -> bool:
        """
        Publish with retained flag.
        """
        __use_as_is__ = False
        __translation__ = "{0}.publish({1}.c_str(), {2}.c_str(), {3})"
        return False

    def subscribe(self, topic: str) -> bool:
        """
        Subscribe to a topic (QoS 0).
        """
        __use_as_is__ = False
        __translation__ = "{0}.subscribe({1}.c_str())"
        return False

    def subscribe_with_qos(self, topic: str, qos: int) -> bool:
        """
        Subscribe with a specific QoS.
        """
        __use_as_is__ = False
        __translation__ = "{0}.subscribe({1}.c_str(), {2})"
        return False

    def unsubscribe(self, topic: str) -> bool:
        """
        Unsubscribe from a topic.
        """
        __use_as_is__ = False
        __translation__ = "{0}.unsubscribe({1}.c_str())"
        return False

    def connected(self) -> bool:
        """
        Check if still connected to the MQTT broker.
        """
        __use_as_is__ = True
        __translation__ = "{0}.connected()"

    def disconnect(self) -> None:
        """
        Disconnect from the broker.
        """
        __use_as_is__ = True
        __translation__ = "{0}.disconnect()"

    def loop(self) -> None:
        """
        Handle incoming messages and maintain connection.
        Must be called regularly in `loop()`.
        """
        __use_as_is__ = True
        __translation__ = "{0}.loop()"

    def set_keep_alive(self, keepalive_secs: int) -> None:
        """
        Set MQTT keep-alive interval (seconds).
        """
        __use_as_is__ = True
        __translation__ = "{0}.setKeepAlive({1})"

    def setSocketTimeout(self, timeout_secs: int) -> None:
        """
        Set socket timeout in seconds.
        """
        __use_as_is__ = True
        __translation__ = "{0}.setSocketTimeout({1})"

    def set_buffer_size(self, size: int) -> None:
        """
        Set internal MQTT buffer size (bytes).
        """
        __use_as_is__ = True
        __translation__ = "{0}.setBufferSize({1})"
