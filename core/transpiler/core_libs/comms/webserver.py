__include_modules__ = {"espressif8266": "ESP8266WebServer", "espressif32": "WebServer"}

"""__include_internal_modules__ = {
    "espressif8266": "helpers/webserver/WebserverHelperESP8266",
    "espressif32": "helpers/webserver/WebserverHelperESP32",
}"""

__include_internal_modules__ = "helpers/WebserverHelper"
__dependencies__ = ""  # Built-in to ESP32/ESP8266 Arduino cores


class WebServer:
    """
    Dummy class for ESP32/ESP8266 synchronous WebServer.

    This class provides a simple HTTP server with support for GET/POST routes.
    It is blocking and should be used for lightweight traffic only.
    """

    def __init__(self, port: int = 80):
        """
        Initializes the WebServer on a specified port.

        Args:
            port (int): Port number to listen on (usually 80).
        """
        __use_as_is__ = False
        __is_reference__ = False
        __class_actual_type__ = {
            "espressif8266": "ESP8266WebServer",
            "espressif32": "WebServer",
        }
        __construct_with_equal_to__ = (
            False  # this means is constructs like WebServer server(80)
        )
        __translation__ = "({port})"
        pass

    def on(self, path: str, method: str, handler: callable) -> WebServer:
        """
        Registers a handler function for the given URL path.

        Args:
            path (str): The URL endpoint (e.g., "/status").
            method (str): "HTTP_GET" or "HTTP_POST"
            handler (callable): A function with no parameters that handles the request.

        Example:
            server.on("/hello", handle_hello)
        """
        __use_as_is__ = False
        __translation__ = "custom_webserver_on({self}, {path}, {method}, {handler})"
        pass

    def begin(self) -> WebServer:
        """
        Starts the web server. Must be called after all routes are registered.
        """
        __use_as_is__ = True
        __translation__ = "{self}.begin()"
        pass

    def handle_client(self) -> WebServer:
        """
        Processes incoming client requests. Should be called repeatedly in loop().
        """
        __use_as_is__ = True
        __translation__ = "{self}.handleClient()"
        pass

    def send(self, status_code: int, content_type: str, body: str) -> None:
        """
        Sends an HTTP response to the client.

        Args:
            status_code (int): HTTP status code (e.g., 200, 404).
            content_type (str): MIME type (e.g., "text/plain").
            body (str): The response body.
        """
        __use_as_is__ = False
        __translation__ = (
            "{self}.send({status_code}, {content_type}.c_str(), {body}.c_str())"
        )
        pass

    def has_arg(self, name: str) -> bool:
        """
        Checks if a parameter was passed in the HTTP request.

        Args:
            name (str): The name of the parameter.

        Returns:
            bool: True if parameter exists, False otherwise.
        """
        __use_as_is__ = False
        __translation__ = "{self}.hasArg({name}.c_str())"
        return False

    def arg(self, name: str) -> str:
        """
        Retrieves the value of a parameter from the HTTP request.

        Args:
            name (str): The name of the parameter.

        Returns:
            str: The value of the parameter.
        """
        __use_as_is__ = False
        __translation__ = "{self}.arg({name}.c_str())"
        return ""
