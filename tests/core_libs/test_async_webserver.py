import comms.async_webserver as aw


# --- Global objects ---
server = aw.AsyncWebServer(port=80)


def handle_root(request: aw.AsyncWebServerRequest) -> None:
    request.send(200, "text/plain", "Hello from ESP!")
    request.arg("test")
    request.has_param("test")


def my_filter(req: aw.AsyncWebServerRequest) -> bool:
    return True


def my_callback(req: aw.AsyncWebServerRequest) -> None:
    handle_root(req)


def setup() -> None:
    # Basic route and server start
    server.on("/", "HTTP_GET", handle_root)
    server.begin()

    # Static file serving setup
    st = server.serve_static("/files", "/")
    st.set_default_file("testfile.txt")
    st.set_cache_control(864000)
    st.set_last_modified(100)
    handler = st.set_authentication("user", "password")

    # AsyncWebHandler tests

    handler.is_request_handler_trivial()
    handler.set_authentication("admin", "pass")
    handler.set_filter(my_filter)


def loop() -> None:
    # Minimal loop stub
    pass
