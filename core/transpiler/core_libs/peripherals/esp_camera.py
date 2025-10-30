"""
ESP32 Camera Peripheral
=======================

This module provides a Python-style abstraction for the **ESP32 Camera Peripheral**, 
enabling you to easily capture photos, stream video, and upload images via HTTP.  
It wraps Espressif’s low-level `esp_camera` driver and provides high-level access 
through the `Camera` and `Image` classes.

**Features**
- Initialize and configure ESP32 camera (OV2640 and compatible modules)
- Capture still frames and save locally or upload via HTTP
- Convert captured images to Base64 (for MQTT/JSON payloads)
- Start an HTTP MJPEG stream server
- Automatically manage PSRAM usage and frame buffers

**Dependencies**
- ESP32 Arduino Core (`esp_camera.h`, `WiFi.h`, `HTTPClient.h`)
- Internal helper: none (self-contained)
- Requires hardware camera pins defined in C++ `Camera.h`

**Sample Code**
```python
import peripherals.camera as cam_mod

cam = cam_mod.Camera("VGA", "JPEG")

def setup() -> None:

    #wifi connection is required for http.
    while not cam.is_wifi_connected():
        cam.wifi_connect("<ssid>", "<password>")
    if cam.begin():
        img = cam.capture()
        img.save("/photo.jpg")
        cam.send_http("http://example.com/upload")

def loop() -> None:
    pass
```
"""
__include_modules__ = "esp_camera,WiFi,HTTPClient"
__include_internal_modules__ = "helpers/peripherals/ESPCameraHelper"
__dependencies__ = "espressif/esp32-camera"
__available_platforms__ = "espressif32"


class Image:
    """
    Represents a captured image frame from the ESP32 camera.
    Provides convenient methods to save, encode, and inspect the image.
    """

    def __init__(self) -> None:
        """
        Creates an empty image container.

        Normally returned by `Camera.capture()`.
        """
        __use_as_is__ = True

    def save(self, path: str) -> None:
        """
        Save the captured image to SPIFFS or SD card.

        Args:
            path (str): File path, e.g. "/photo.jpg"
        """
        __use_as_is__ = False
        __translation__ = "{0}.save({1})"

    def base64(self) -> str:
        """
        Convert image data to Base64-encoded string.

        Returns:
            str: Base64-encoded representation of the image
        """
        __use_as_is__ = False
        __translation__ = "{0}.base64()"
        return ""

    def size(self) -> int:
        """
        Get image size in bytes.

        Returns:
            int: Image size
        """
        __use_as_is__ = False
        __translation__ = "{0}.size()"
        return 0

    def get_width(self) -> int:
        """
        Get image width in pixels.

        Returns:
            int: Width
        """
        __use_as_is__ = False
        __translation__ = "{0}.get_width()"
        return 0

    def get_height(self) -> int:
        """
        Get image height in pixels.

        Returns:
            int: Height
        """
        __use_as_is__ = False
        __translation__ = "{0}.get_height()"
        return 0


class Camera:
    """
    Provides a Pythonic interface to initialize, capture, stream, and upload
    frames from the ESP32 camera module.
    """

    def __init__(self, resolution: str, format: str) -> None:
        """
        Create a Camera instance.

        Args:
            resolution (str): Frame size, e.g. "VGA", "SVGA", "UXGA"
            format (str): Pixel format, e.g. "JPEG", "RGB565"
        """
        __use_as_is__ = False
        __class_actual_type__ = "Camera"
        __construct_with_equal_to__ = True
        __translation__ = "Camera({1}, {2})"

    def wifi_connect(self, ssid: str, password: str) -> bool:
        """
        Connect the ESP32 to a Wi-Fi network.

        Args:
            ssid (str): Wi-Fi SSID.
            password (str): Wi-Fi password.

        Returns:
            bool: True if the connection succeeded, False otherwise.
        """
        __use_as_is__ = False
        __translation__ = "{0}.wifi_connect({1}, {2})"
        return True

    def is_wifi_connected(self) -> bool:
        """
        Check whether the device is currently connected to Wi-Fi.

        Returns:
            bool: True if Wi-Fi is connected.
        """
        __use_as_is__ = False
        __translation__ = "{0}.is_wifi_connected()"
        return True

    def begin(self) -> bool:
        """
        Initialize the camera hardware and configure GPIOs.

        Returns:
            bool: True if successful, False otherwise
        """
        __use_as_is__ = False
        __translation__ = "{0}.begin()"
        return True

    def capture(self) -> Image:
        """
        Capture a still image frame.

        Returns:
            Image: Captured image object
        """
        __use_as_is__ = False
        __translation__ = "{0}.capture()"
        return Image()

    def send_http(self, url: str) -> bool:
        """
        Upload the latest captured image via HTTP POST.

        Args:
            url (str): Target HTTP endpoint

        Returns:
            bool: True if upload succeeded
        """
        __use_as_is__ = False
        __translation__ = "{0}.send_http({1})"
        return True

    def stream_http(self, port: int) -> None:
        """
        Start an MJPEG streaming server.

        Args:
            port (int): Port number for HTTP stream (default: 8080)

        Notes:
            - Accessible via `http://<device_ip>:port`
            - Stream runs indefinitely unless stopped manually
        """
        __use_as_is__ = False
        __translation__ = "{0}.stream_http({1})"

    def deinit(self) -> None:
        """
        Deinitialize and release camera resources.
        """
        __use_as_is__ = False
        __translation__ = "{0}.deinit()"
