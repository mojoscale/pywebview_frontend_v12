import peripherals.esp_camera as ec

# Create instance
camera = ec.Camera("VGA", "JPEG")


def callback() -> None:
    print("got a call")


def setup() -> None:
    # Call all methods
    camera.begin()

    while not camera.is_wifi_connected():
        camera.wifi_connect("Ssid", "password")

    image = camera.capture()

    image.save("/")

    img_base64 = image.base64()

    img_size = image.size()
    img_width = image.get_width()
    img_height = image.get_height()

    did_send_http = camera.send_http("localhost:8000")

    camera.stream_http(8000)

    camera.deinit()


def loop() -> None:
    pass
