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
        __translation__ = "({wifi_client})"
        pass

    def set_server(self, host: str, port: int = 1883) -> None:
        """
        Set the MQTT broker address and port.
        """
        __use_as_is__ = False
        __translation__ = "mqtt_set_server_helper({self}, {host}, {port})"
        pass

    def set_callback(self, callback_func: callable[[str, str], None]) -> None:
        """
        Set the callback function for received MQTT messages.
        """
        __use_as_is__ = False
        __translation__ = "setupSimpleCallback({self}, {callback_func})"
        pass

    def connect(
        self,
        client_id: str,
        username: str = "",
        password: str = "",
        will_topic: str = "",
        will_qos: int = 0,
        will_retain: bool = False,
        will_message: str = "",
    ) -> bool:
        """
        Connect to the MQTT broker using PubSubClient.

        This unified method replaces all connect variants:
          - Simple connect with only `client_id`
          - Connect with authentication
          - Connect with a last will message (with or without auth)

        All parameters are optional except `client_id`.
        The correct underlying overload is automatically chosen
        based on which arguments are provided.

        Args:
            client_id (str): Unique client identifier.
            username (str, optional): MQTT username. Defaults to "".
            password (str, optional): MQTT password. Defaults to "".
            will_topic (str, optional): Topic for the Last Will message. Defaults to "".
            will_qos (int, optional): QoS for the Last Will message. Defaults to 0.
            will_retain (bool, optional): Retain flag for Last Will. Defaults to False.
            will_message (str, optional): Message content for Last Will. Defaults to "".

        Returns:
            bool: True if connection was successful, False otherwise.

        Examples:
            >>> client.connect("esp32_1")
            >>> client.connect("esp32_2", username="user", password="pass")
            >>> client.connect("esp32_3", will_topic="status", will_message="offline")
            >>> client.connect("esp32_4", username="user", password="pass",
            ...                will_topic="status", will_qos=1, will_retain=True,
            ...                will_message="offline")
        """
        __use_as_is__ = False

        # --- Translation logic for the transpiler ---
        __translation__ = "custom_mqtt_connect({self}, {client_id}, {username}, {password}, {will_topic}, {will_qos}, {will_retain}, {will_message})"
        return False

    def publish(self, topic: str, payload: str, retained: bool = False) -> bool:
        """
        Publish a plain string payload to a topic.
        """
        __use_as_is__ = False
        __translation__ = "mqtt_publish_helper({self}, {topic}, {payload}, {retained})"
        return False

    def subscribe(self, topic: str, qos: int = 0) -> bool:
        """
        Subscribe to a topic (QoS 0).
        """
        __use_as_is__ = False
        __translation__ = "mqtt_subscribe_helper({self}, {topic}, {qos})"
        return False

    def unsubscribe(self, topic: str) -> bool:
        """
        Unsubscribe from a topic.
        """
        __use_as_is__ = False
        __translation__ = "mqtt_unsubscribe_helper({self}, {topic})"
        return False

    def connected(self) -> bool:
        """
        Check if still connected to the MQTT broker.
        """
        __use_as_is__ = True
        __translation__ = "{self}.connected()"

    def disconnect(self) -> None:
        """
        Disconnect from the broker.
        """
        __use_as_is__ = True
        __translation__ = "{self}.disconnect()"

    def loop(self) -> None:
        """
        Handle incoming messages and maintain connection.
        Must be called regularly in `loop()`.
        """
        __use_as_is__ = True
        __translation__ = "{self}.loop()"

    def set_keep_alive(self, keepalive_secs: int) -> None:
        """
        Set MQTT keep-alive interval (seconds).
        """
        __use_as_is__ = True
        __translation__ = "{self}.setKeepAlive({keepalive_secs})"

    def setSocketTimeout(self, timeout_secs: int) -> None:
        """
        Set socket timeout in seconds.
        """
        __use_as_is__ = True
        __translation__ = "{self}.setSocketTimeout({timeout_secs})"

    def set_buffer_size(self, size: int) -> None:
        """
        Set internal MQTT buffer size (bytes).
        """
        __use_as_is__ = True
        __translation__ = "{self}.setBufferSize({size})"
