import async_webserver as aw

server = aw.AsyncWebServer(80)


def handle_root(request: aw.AsyncWebServerRequest) -> None:
    request.send(200, "text/plain", "Hello from ESP!")
    request.arg("test")
    request.has_param("test")


def setup() -> None:
    server.on("/", "HTTP_GET", handle_root)
    server.begin()

    st = server.serve_static("/files", "/")

    st.set_default_file("testfile.txt")
    st.set_cache_control(864000)
    st.set_last_modified(100)
    st.set_authentication("user", "password")


def loop() -> None:
    pass
