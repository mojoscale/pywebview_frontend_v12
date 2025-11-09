import comms.webserver as w
import comms.wifi as wi
import core.arduino as ad

# Create instance
server = w.WebServer()


def callback() -> None:
    print("got a call")


def setup() -> None:
    # Call all methods
    while not wi.wifi_is_connected:
        wi.wifi_begin("ssid", "pass")
        ad.delay(1000)
        print(f"connecting....")
    server.on("/test", "HTTP_GET", callback)
    server.begin()
    server.handle_client()
    server.send(200, "text/plain", "Hello")
    has_param = server.has_arg("test")
    arg_value = server.arg("param")


def loop() -> None:
    pass
