"""
BLESimple
=========

A lightweight abstraction layer that simulates Bluetooth Low Energy (BLE)
operations for both **Central** and **Peripheral** roles.

This class provides a Python-like API for creating, managing, and interacting
with BLE devices. It is designed to serve as a stub for generating or simulating
BLE logic in microcontroller environments such as ESP32 or similar boards.

Supported Features
------------------
- Initialize BLE in `central` or `peripheral` mode.
- Start/stop advertising or scanning.
- Connect and disconnect devices.
- Define services and characteristics.
- Read, write, and notify characteristic values.
- Register callbacks for connection, disconnection, write, and notify events.

Example Usage
-------------
```python
# Initialize as a peripheral
ble = BLESimple("MyDevice", "peripheral")

# Inside setup()
ble.init_ble()
ble.add_service("1234")
ble.add_characteristic("1234", "5678", "Hello", readable=True, writable=True, notify=True)
ble.start()

# Handle incoming writes
def on_write_handler(value: str):
    print("Central wrote:", value)

ble.on_write("5678", on_write_handler)```
"""

__include_modules__ = "BLESimple"
__include_internal_modules__ = ""
__dependencies__ = ""


class BLESimple:
    def __init__(self, name: str, mode: str):
        """
        Initialize a BLE device in either 'central' or 'peripheral' mode.

        Args:
            name (str): The name of the BLE device.
            mode (str): 'peripheral' or 'central'.
        """
        __use_as_is__ = False
        __construct_with_equal_to__ = False
        __translation__ = "({1}, {2})"

    def init_ble(self) -> None:
        """
        Custom Initializer, call this inside setup.
        """
        __use_as_is__ = True

    def start(self) -> None:
        """Start BLE advertising or scanning based on the mode."""
        __use_as_is__ = False
        __translation__ = "{0}.start()"

    def stop(self) -> None:
        """Stop BLE services or connections."""
        __use_as_is__ = False
        __translation__ = "{0}.stop()"

    def scan(self, timeout: int) -> list[str]:
        """
        Scan for nearby BLE devices (central mode only).

        Args:
            timeout (int): Scan duration in seconds.

        Returns:
            list[str]: List of device names or IDs.
        """
        __use_as_is__ = False
        __translation__ = "{0}.scan({1})"
        return []

    def get_device_info(self) -> dict[str, str]:
        """
        Get metadata about this device. All values are strings.

        Returns:
            dict[str, str]: A dictionary containing:
                - 'name': Device name
                - 'mode': 'central' or 'peripheral'
                - 'connected': 'True' or 'False' (as string)
        """
        __use_as_is__ = False
        __translation__ = "{0}.get_device_info()"
        return {}

    def connect_to(self, name_or_uuid: str) -> bool:
        """
        Connect to a BLE device by name or UUID.

        Args:
            name_or_uuid (str): Target device ID.

        Returns:
            bool: True if successful.
        """
        __use_as_is__ = False
        __translation__ = "{0}.connect_to({1})"
        return False

    def disconnect(self) -> None:
        """Disconnect from any connected BLE device."""
        __use_as_is__ = False
        __translation__ = "{0}.disconnect()"

    def is_connected(self) -> bool:
        """
        Check if device is currently connected.

        Returns:
            bool: Connection status.
        """
        __use_as_is__ = False
        __translation__ = "{0}.is_connected()"
        return False

    def add_service(self, uuid: str) -> None:
        """
        Define a BLE service (peripheral mode only).

        Args:
            uuid (str): UUID of the service.
        """
        __use_as_is__ = False
        __translation__ = "{0}.add_service({1})"

    def add_characteristic(
        self,
        service_uuid: str,
        uuid: str,
        value: str,
        readable: bool,
        writable: bool,
        notify: bool,
    ) -> None:
        """
        Add a characteristic to the last-defined service.

        Args:
            service_uuid: UUID of service to be added in.
            uuid (str): UUID of the characteristic.
            value (str): Default value.
            readable (bool): Whether central can read.
            writable (bool): Whether central can write.
            notify (bool): Whether peripheral can send notify updates.
        """
        __use_as_is__ = False
        __translation__ = "{0}.add_characteristic({1}, {2}, {3}, {4}, {5})"

    def read(self, uuid: str) -> str:
        """
        Read a characteristic value.

        Args:
            uuid (str): Characteristic UUID.

        Returns:
            str: Value.
        """
        __use_as_is__ = False
        __translation__ = "{0}.read({1})"
        return ""

    def write(self, uuid: str, value: str) -> None:
        """
        Write a value to a characteristic.

        Args:
            uuid (str): Characteristic UUID.
            value (str): Value to write.
        """
        __use_as_is__ = False
        __translation__ = "{0}.write({1}, {2})"

    def notify(self, uuid: str, value: str) -> None:
        """
        Send a notification to subscribers.

        Args:
            uuid (str): Characteristic UUID.
            value (str): Value to send.
        """
        __use_as_is__ = False
        __translation__ = "{0}.notify({1}, {2})"

    def on_connect(self, callback) -> None:
        """
        Register a function to call on connection.

        Args:
            callback (callable): Function with **no arguments**.
                Example:
                    def handler(): ...
        """
        __use_as_is__ = False
        __translation__ = "{0}.on_connect({1})"

    def on_disconnect(self, callback) -> None:
        """
        Register a function to call on disconnect.

        Args:
            callback (callable): Function with **no arguments**.
                Example:
                    def handler(): ...
        """
        __use_as_is__ = False
        __translation__ = "{0}.on_disconnect({1})"

    def on_write(self, uuid: str, callback) -> None:
        """
        Set a callback for write events.

        Args:
            uuid (str): Characteristic UUID.
            callback (callable): Function that takes **one argument (str)** – the value written by central.
                Example:
                    def handler(value: str): ...
        """
        __use_as_is__ = False
        __translation__ = "{0}.on_write({1}, {2})"

    def on_notify(self, uuid: str, callback) -> None:
        """
        Set a callback for notify events.

        Args:
            uuid (str): Characteristic UUID.
            callback (callable): Function that takes **one argument (str)** – the notified value received.
                Example:
                    def handler(value: str): ...
        """
        __use_as_is__ = False
        __translation__ = "{0}.on_notify({1}, {2})"

    def get_services(self) -> list[str]:
        """
        Return all known service UUIDs.

        Returns:
            list[str]: UUIDs
        """
        __use_as_is__ = False
        __translation__ = "{0}.get_services()"
        return []

    def get_characteristics(self, service_uuid: str) -> list[str]:
        """
        Return characteristics under a given service.

        Args:
            service_uuid (str): Service UUID.

        Returns:
            list[str]: Characteristic UUIDs.
        """
        __use_as_is__ = False
        __translation__ = "{0}.get_characteristics({1})"
        return []
