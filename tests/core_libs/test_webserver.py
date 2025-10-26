import comms.webserver as w

# Create instance
server = w.WebServer(80)


def callback() -> None:
    print("got a call")


def setup() -> None:
    # Call all methods
    server.on("/test", "HTTP_GET", callback)
    server.begin()
    server.handle_client()
    server.send(200, "text/plain", "Hello")
    has_param = server.has_arg("test")
    arg_value = server.arg("param")


def loop() -> None:
    pass
