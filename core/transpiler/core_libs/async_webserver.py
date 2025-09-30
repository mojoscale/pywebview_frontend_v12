#__include_modules__ = "ESPAsyncWebServer"

__include_modules__ = {"espressif8266":"ESPAsyncWebServer", 
"espressif32":"ESPAsyncWebServer,AsyncTCP"}
__include_internal_modules__ = ""
__dependencies__ = "me-no-dev/ESPAsyncWebServer,me-no-dev/AsyncTCP"


class AsyncWebServerRequest:
    """
    Dummy for AsyncWebServerRequest* in ESPAsyncWebServer.

    This class simulates methods available in an HTTP request object
    for async handling on ESP32/ESP8266.

    """

    def __init__(self):
        __pass_as__="pointer"
        __class_actual_type__ = ""
        

    def send(self, status_code: int, content_type: str, body: str) -> None:
        """
        Sends a response to the HTTP client.

        Args:
            status_code (int): HTTP status code (e.g., 200, 404).
            content_type (str): MIME type of the response (e.g., "text/html").
            body (str): Response body content.

        Returns:
            None
        """
        __use_as_is__ = False
        __translation__ = "{0}->send({1}, {2}.c_str(), {3}.c_str())"

        pass

    def arg(self, name: str) -> str:
        """
        Gets the value of a URL parameter or POST argument by name.

        Args:
            name (str): Name of the argument to retrieve.

        Returns:
            str: Value of the argument or empty string if not found.
        """
        __use_as_is__ = False
        __translation__ = "{0}->arg({1}.c_str())"
        return ""

    def has_param(self, name: str) -> bool:
        """
        Checks if a given parameter exists in the request.

        Args:
            name (str): Name of the parameter.

        Returns:
            bool: True if parameter exists, False otherwise.
        """
        __use_as_is__ = False
        __translation__ = "{0}->hasParam({1}.c_str())"
        return False


class AsyncWebServer:
    """
    Dummy for AsyncWebServer.

    Represents the HTTP server for asynchronous request handling.
    """

    def __init__(self, port: int):
        """
        Initializes the server on a given port.

        Args:
            port (int): Port number for the HTTP server (e.g., 80).
        """
        __use_as_is__ = False
        __translation__ = "({1})"
        __class_actual_type__ = "AsyncWebServer"
        __construct_with_equal_to__ = False
        __pass_as__="reference"
        pass

    def on(self, path: str, method: str, handler) -> None:
        """
        Registers a request handler for a specific path and method.

        Args:
            path (str): The URL path to handle.
            method (str): HTTP method as string (e.g., "GET", "POST").
            handler (function): Function to call when the request is received.

        Returns:
            None
        """
        __use_as_is__ = False
        __translation__ = "{0}.on({1}.c_str(), {2}, {3})"
        pass

    def begin(self) -> None:
        """
        Starts the server. Must be called after all routes are registered.

        Returns:
            None
        """
        __use_as_is__ = True
        pass

    def serve_static(self, uri: str, fs, path: str, cache_control: str) -> None:
        """
        Serves static files from the filesystem at a given URI.

        Args:
            uri (str): The URL path prefix (e.g., "/static").
            fs: Filesystem reference (e.g., LittleFS).
            path (str): The root directory in the FS.
            cache_control (str): Cache control header value.

        Returns:
            None
        """
        __use_as_is__ = False
        __translation__ = "custom_serve_static({0}, {1}.c_str(), LITTLEFS, {2}.c_str(), {3})"
        pass
