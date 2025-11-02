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
        __translation__ = "{self}.save({path})"

    def base64(self) -> str:
        """
        Convert image data to Base64-encoded string.

        Returns:
            str: Base64-encoded representation of the image
        """
        __use_as_is__ = False
        __translation__ = "{self}.base64()"
        return ""

    def size(self) -> int:
        """
        Get image size in bytes.

        Returns:
            int: Image size
        """
        __use_as_is__ = False
        __translation__ = "{self}.size()"
        return 0

    def get_width(self) -> int:
        """
        Get image width in pixels.

        Returns:
            int: Width
        """
        __use_as_is__ = False
        __translation__ = "{self}.get_width()"
        return 0

    def get_height(self) -> int:
        """
        Get image height in pixels.

        Returns:
            int: Height
        """
        __use_as_is__ = False
        __translation__ = "{self}.get_height()"
        return 0


class Camera:
    """
    Provides a Pythonic interface to initialize, capture, stream, and upload
    frames from the ESP32 camera module.
    """

    def __init__(self, resolution: str = "VGA", format: str = "JPEG") -> None:
        """
        Create a new Camera instance for the ESP32-CAM module.

        This constructor sets up the desired **frame resolution** and **pixel format**
        for image capture. It does not initialize the hardware yet — call
        `begin()` or `begin_custom()` afterward to configure GPIOs and start
        the camera driver.

        Args:
            resolution (str, optional):
                Output frame size (image resolution).
                Supported values (from smallest to largest):

                - `"QQVGA"` — 160 × 120
                - `"QVGA"` — 320 × 240
                - `"VGA"` — 640 × 480 (default)
                - `"SVGA"` — 800 × 600
                - `"XGA"` — 1024 × 768
                - `"SXGA"` — 1280 × 1024
                - `"UXGA"` — 1600 × 1200

                Larger resolutions require more memory and PSRAM support.

            format (str, optional):
                Image pixel format (color encoding).
                Supported values:

                - `"JPEG"` — Compressed image format (default, best for transmission)
                - `"RGB565"` — 16-bit RGB color format
                - `"YUV422"` — YUV color encoding (4:2:2 sampling)
                - `"GRAYSCALE"` — Single-channel grayscale

                Use `"JPEG"` for most use cases such as HTTP streaming or snapshots.

        Returns:
            None

        Example:
            ```python
            import peripherals.camera as cam

            # Create a camera for 800×600 JPEG capture
            camera = cam.Camera("SVGA", "JPEG")

            # Create a grayscale camera for analytics
            graycam = cam.Camera("QVGA", "GRAYSCALE")
            ```
        """
        __use_as_is__ = False
        __class_actual_type__ = "Camera"
        __construct_with_equal_to__ = True
        __translation__ = "Camera({resolution}, {format})"

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
        __translation__ = "{self}.wifi_connect({ssid}, {password})"
        return True

    def is_wifi_connected(self) -> bool:
        """
        Check whether the device is currently connected to Wi-Fi.

        Returns:
            bool: True if Wi-Fi is connected.
        """
        __use_as_is__ = False
        __translation__ = "{self}.is_wifi_connected()"
        return True

    def begin(self, variant_name: str = "AI_THINKER") -> bool:
        """
        Initialize the ESP32 camera using a predefined pin configuration variant.

        This method provides a simple way to start the camera by specifying
        a known hardware variant name (such as `"AI_THINKER"`, `"WROVER"`, or `"M5STACK"`).
        Internally, the correct GPIO mappings for that board are automatically
        selected and used to configure the camera sensor and data pins.

        Args:
            variant_name (str):
                Name of the ESP32 camera module variant.
                Supported values include:
                  - "AI_THINKER"
                  - "WROVER"
                  - "M5STACK"

                If the provided name does not match a known variant, the
                default `"AI_THINKER"` mapping is used.

        Returns:
            bool: True if the camera was initialized successfully, False otherwise.

        Example:
            ```python
            import peripherals.camera as cam

            camera = cam.Camera("VGA", "JPEG")
            ok = camera.begin("AI_THINKER")
            if ok:
                print("Camera ready!")
            else:
                print("Camera failed to initialize.")
            ```
        """
        __use_as_is__ = False
        __translation__ = "{self}.begin({variant_name})"
        return True

    def begin_custom(
        self,
        pin_pwdn: int = -1,
        pin_reset: int = -1,
        pin_xclk: int = 0,
        pin_sscb_sda: int = 26,
        pin_sscb_scl: int = 27,
        pin_d7: int = 35,
        pin_d6: int = 34,
        pin_d5: int = 39,
        pin_d4: int = 36,
        pin_d3: int = 21,
        pin_d2: int = 19,
        pin_d1: int = 18,
        pin_d0: int = 5,
        pin_vsync: int = 25,
        pin_href: int = 23,
        pin_pclk: int = 22,
    ) -> bool:
        """
        Initialize the ESP32 camera using a fully custom pin configuration.

        This function exposes **every hardware pin** explicitly and can be
        called using keyword arguments for flexibility. All parameters are
        optional and have sensible defaults (AI Thinker layout).

        Args:
            pin_pwdn (int): Power-down control pin. Defaults to -1.
            pin_reset (int): Reset pin. Defaults to -1.
            pin_xclk (int): External clock pin (ESP32 → camera). Defaults to 0.
            pin_sscb_sda (int): SCCB (I2C data). Defaults to 26.
            pin_sscb_scl (int): SCCB (I2C clock). Defaults to 27.
            pin_d7 (int): Pixel data bit 7 (MSB). Defaults to 35.
            pin_d6 (int): Pixel data bit 6. Defaults to 34.
            pin_d5 (int): Pixel data bit 5. Defaults to 39.
            pin_d4 (int): Pixel data bit 4. Defaults to 36.
            pin_d3 (int): Pixel data bit 3. Defaults to 21.
            pin_d2 (int): Pixel data bit 2. Defaults to 19.
            pin_d1 (int): Pixel data bit 1. Defaults to 18.
            pin_d0 (int): Pixel data bit 0 (LSB). Defaults to 5.
            pin_vsync (int): Vertical sync signal. Defaults to 25.
            pin_href (int): Horizontal reference signal. Defaults to 23.
            pin_pclk (int): Pixel clock signal. Defaults to 22.

        Returns:
            bool: True if the camera initialized successfully, False otherwise.

        Example:
            ```python
            camera.begin_custom(
                pin_pwdn=32,
                pin_reset=-1,
                pin_xclk=0,
                pin_sscb_sda=26,
                pin_sscb_scl=27,
                pin_d7=35, pin_d6=34, pin_d5=39, pin_d4=36,
                pin_d3=21, pin_d2=19, pin_d1=18, pin_d0=5,
                pin_vsync=25, pin_href=23, pin_pclk=22
            )
            ```
        """
        __use_as_is__ = False
        __translation__ = "{self}.begin_custom({pin_pwdn}, {pin_reset}, {pin_xclk}, {pin_sscb_sda}, {pin_sscb_scl}, {pin_d7}, {pin_d6}, {pin_d5}, {pin_d4}, {pin_d3}, {pin_d2}, {pin_d1}, {pin_d0}, {pin_vsync}, {pin_href}, {pin_pclk})"
        return True

    def capture(self) -> Image:
        """
        Capture a still image frame.

        Returns:
            Image: Captured image object
        """
        __use_as_is__ = False
        __translation__ = "{self}.capture()"
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
        __translation__ = "{self}.send_http({url})"
        return True

    def stream_http(self, port: int = 8080) -> None:
        """
        Start an MJPEG streaming server.

        Args:
            port (int): Port number for HTTP stream (default: 8080)

        Notes:
            - Accessible via `http://<device_ip>:port`
            - Stream runs indefinitely unless stopped manually
        """
        __use_as_is__ = False
        __translation__ = "{self}.stream_http({port})"

    def deinit(self) -> None:
        """
        Deinitialize and release camera resources.
        """
        __use_as_is__ = False
        __translation__ = "{self}.deinit()"
