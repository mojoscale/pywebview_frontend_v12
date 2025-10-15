# __include_modules__ = "ESPAsyncWebServer"

__include_modules__ = {
    "espressif8266": "ESPAsyncWebServer,LITTLEFS",
    "espressif32": "ESPAsyncWebServer,AsyncTCP",
}
__include_internal_modules__ = "helpers/AsyncWebServerHelper"
__dependencies__ = "me-no-dev/ESPAsyncWebServer,me-no-dev/AsyncTCP"


class AsyncWebServerRequest:
    """ """

    def __init__(self):
        """
            Initializes a new instance of the asynchronous HTTP server.

        This constructor creates an `AsyncWebServer` object bound to a specific
        network port. Once instantiated, you can register HTTP route handlers
        using the `on()` method and start the server with `begin()`.

        This class serves as a Python stub for the C++ `AsyncWebServer` class from
        the **ESPAsyncWebServer** library, commonly used on ESP32 and ESP8266 boards.
        The actual implementation is handled by the corresponding C++ library when
        the transpiler generates the final firmware code.

        **Usage Example (Python → Arduino Transpilation):**
            ```python
            import async_webserver as a

            server = a.AsyncWebServer(80)

            def handle_root(request:a.AsyncWebServerRequest) -> None:
                request.send(200, "text/plain", "Hello from ESP!")


            def setup()->None:
                server.on("/", HTTP_GET, handle_root)
                server.begin()


            def loop()->None:
                pass
            ```


        Args:
            port (int):
                The TCP port number on which the HTTP server will listen.
                Typically, 80 is used for standard HTTP and 443 for HTTPS.
        Returns:
            None
        """
        __is_pointer__ = True
        __pass_as__ = "pointer"
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


class AsyncWebHandler:
    """
    Python representation of the C++ `AsyncWebHandler` class from ESPAsyncWebServer.

    This class acts as an abstract base for web request handlers such as
    `AsyncStaticWebHandler` or `AsyncCallbackWebHandler`.

    It provides methods for:
      - Determining whether a handler can process a given request.
      - Executing the request handler.
      - Applying authentication and filters.
      - Controlling handler priority and behavior.

    Note:
        This class should generally not be instantiated directly.
        Instead, use subclasses that implement `can_handle()` and `handle_request()`.
    """

    def __init__(self):
        """
        Initialize an AsyncWebHandler instance.

        This constructor sets `__use_as_is__` to False,
        meaning the transpiler should not instantiate this class directly.
        """
        __use_as_is__ = False
        __pass_as__ = "reference"

    # --- Core Handler Methods ---

    def can_handle(self, request: AsyncWebServerRequest) -> bool:
        """
        Determine whether this handler can process the incoming request.

        Args:
            request (AsyncWebServerRequest): The HTTP request object.

        Returns:
            bool: True if the handler can handle the request; False otherwise.

        Translation:
            {0}.canHandle({1})
        """
        __translation__ = "{0}.canHandle({1})"

    def handle_request(self, request: AsyncWebServerRequest) -> None:
        """
        Handle the incoming web request.

        Args:
            request (AsyncWebServerRequest): The HTTP request to process.

        Translation:
            {0}.handleRequest({1})
        """
        __translation__ = "{0}.handleRequest({1})"

    def is_request_handler_trivial(self) -> bool:
        """
        Check whether this handler performs trivial (lightweight) processing.

        Returns:
            bool: True if the handler is trivial; False otherwise.

        Translation:
            {0}.isRequestHandlerTrivial()
        """
        __translation__ = "{0}.isRequestHandlerTrivial()"

    # --- Authentication Methods ---

    def set_authentication(self, username: str, password: str) -> AsyncWebHandler:
        """
        Protect this handler with basic authentication.

        Args:
            username (str): The HTTP Basic Auth username.
            password (str): The HTTP Basic Auth password.

        Returns:
            AsyncWebHandler: The same handler instance (for chaining).

        Translation:
            {0}.setAuthentication({1}, {2})
        """
        __translation__ = "{0}.setAuthentication({1}, {2})"

    # --- Filtering ---

    def set_filter(self, filter_func) -> AsyncWebHandler:
        """
        Assign a filter function that decides if this handler should process a request.

        Args:
            filter_func (ArRequestFilterFunction): The filtering function.

        Returns:
            AsyncWebHandler: The same handler instance (for chaining).

        Translation:
            {0}.setFilter({1})
        """
        __translation__ = "{0}.setFilter({1})"

    def filter(self, request: AsyncWebServerRequest) -> bool:
        """
        Run the filter function associated with this handler.

        Args:
            request (AsyncWebServerRequest): The request to evaluate.

        Returns:
            bool: True if the handler should process this request.

        Translation:
            {0}.filter({1})
        """
        __translation__ = "{0}.filter({1})"

    # --- Priority ---

    def set_priority(self, priority: int) -> AsyncWebHandler:
        """
        Assign a priority level to this handler.

        Args:
            priority (int): The priority value (higher = earlier execution).

        Returns:
            AsyncWebHandler: The same handler instance (for chaining).

        Translation:
            {0}.setPriority({1})
        """
        __translation__ = "{0}.setPriority({1})"

    def priority(self) -> int:
        """
        Get the priority value assigned to this handler.

        Returns:
            int: The priority level.

        Translation:
            {0}.priority()
        """
        __translation__ = "{0}.priority()"

    # --- Request Callback (Optional) ---

    def on_request(self) -> AsyncWebHandler:
        """
        Assign a custom callback to handle incoming requests.

        Args:
            callback (ArRequestHandlerFunction): The function that processes the request.

        Returns:
            AsyncWebHandler: The same handler instance (for chaining).

        Translation:
            {0}.onRequest({1})
        """
        __translation__ = "{0}.onRequest({1})"


class AsyncStaticWebHandler:
    """
    Represents a static file handler returned by `AsyncWebServer.serve_static()`.

    This class allows chaining configuration methods such as
    `set_default_file()`, `set_cache_control()`, `set_last_modified()`,
    and `set_authentication()`.

    Example:
        ```python
        server.serve_static("/", "/www", 86400) \
              .set_default_file("index.html") \
              .set_authentication("user", "pass")
        ```
    """

    def __init__(self):
        """
        This class should not be instantiated directly.

        Instances are automatically returned when calling
        `AsyncWebServer.serve_static()`.
        """
        __use_as_is__ = False
        __pass_as__ = "reference"
        __class_actual_type__ = "AsyncStaticWebHandler"

    def set_default_file(self, filename: str) -> AsyncStaticWebHandler:
        """
        Sets the default file to serve when a directory is requested.

        Args:
            filename (str): The file name to serve by default
                (e.g., "index.html").

        Returns:
            AsyncStaticWebHandler: Reference to the same handler (for chaining).




        """
        __use_as_is__ = False
        __translation__ = "{0}.setDefaultFile({1}.c_str())"
        return self

    def set_cache_control(self, cache_seconds: int) -> AsyncStaticWebHandler:
        """
        Sets the cache control duration for static files.

        Args:
            cache_seconds (int): Number of seconds that the browser
                should cache the file (e.g., 86400 for one day).

        Returns:
            AsyncStaticWebHandler: Reference to the same handler (for chaining).

        Notes:
            Transpiles to:
                `.setCacheControl("max-age=<cache_seconds>")`
        """
        __use_as_is__ = False
        __translation__ = "setCacheControlSeconds({0}, {1})"
        return self

    def set_last_modified(self, timestamp: int) -> AsyncStaticWebHandler:
        """
        Sets the 'Last-Modified' timestamp header for the served files.

        Args:
            timestamp (int): UNIX timestamp representing the last
                modification time.

        Returns:
            AsyncStaticWebHandler: Reference to the same handler (for chaining).
        """
        __use_as_is__ = False
        __translation__ = "{0}.setLastModified({1})"
        return self

    def set_authentication(self, user: str, password: str) -> AsyncWebHandler:
        """
        Sets basic HTTP authentication credentials for the static route.

        Args:
            user (str): Username required to access the files.
            password (str): Corresponding password.

        Returns:
            AsyncStaticWebHandler: Reference to the same handler (for chaining).
        """
        __use_as_is__ = False
        __translation__ = "{0}.setAuthentication({1}.c_str(), {2}.c_str())"
        return self


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
        # __translation__ = "{0}.on({1}.c_str(), {2}, {3})"
        __translation__ = "async_server_on({0}, {1}, {2}, {3})"
        pass

    def begin(self) -> None:
        """
        Starts the server. Must be called after all routes are registered.

        Returns:
            None
        """
        __use_as_is__ = True
        __translation__ = "{0}.begin()"
        pass

    def serve_static(self, uri: str, file_path: str) -> AsyncStaticWebHandler:
        """
        Serves static files from the filesystem at a given URI.

        Args:
            uri (str): The URL path prefix (e.g., "/static").
            path (str): The root directory in the FS.
            cache_control (str): Cache control header value.

        Returns:
            None
        """
        __use_as_is__ = False
        __translation__ = "custom_serve_static({0}, {1}, {2})"
