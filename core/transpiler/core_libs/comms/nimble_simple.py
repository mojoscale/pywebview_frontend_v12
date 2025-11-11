__include_modules__ = "NimBLESimple"
__include_internal_modules__ = ""
__dependencies__ = "h2zero/NimBLE-Arduino"
__available_platforms__ = "espressif32"


class NimBLESimple:
    def __init__(self, name: str, service_uuid: str, char_uuid: str):
        """
        Initialize a unified BLE peripheral on ESP32 using NimBLE.

        Args:
            name (str): Device name to advertise.
            service_uuid (str): UUID of the primary BLE service.
            char_uuid (str): UUID of the primary characteristic.
        """
        __use_as_is__ = False
        __construct_with_equal_to__ = False
        __translation__ = "({name}, {service_uuid}, {char_uuid})"

    # -------------------------------------------------------------------------
    # Core lifecycle
    # -------------------------------------------------------------------------

    def begin(self, is_read=True, is_write=True, is_notify=True) -> None:
        """
        Initialize the NimBLE stack, create server/service/characteristic,
        and start advertising.
        """
        __use_as_is__ = False
        __translation__ = "{self}.begin({is_read}, {is_write}, {is_notify})"

    def stop(self) -> None:
        """
        Stop advertising, disconnect clients, and deinitialize BLE.
        """
        __use_as_is__ = False
        __translation__ = "{self}.stop()"

    # -------------------------------------------------------------------------
    # Data send / receive
    # -------------------------------------------------------------------------

    def send(self, data: str) -> None:
        """
        Send data to the connected BLE central using notification.

        Args:
            data (str): Text or binary payload to send.
        """
        __use_as_is__ = False
        __translation__ = "{self}.send({data})"

    def set_connect_callback(self, callback: callable[[str], None]) -> None:
        __translation__ = "{self}.setConnectCallback({callback})"

    def set_disconnect_callback(self, callback: callable[[str], None]) -> None:
        __translation__ = "{self}.setDisconnectCallback({callback})"

    def set_write_callback(self, callback: callable[[str], None]) -> None:
        __translation__ = "{self}.setWriteCallback({callback})"

    def set_read_callback(self, callback: callable[[], None]) -> None:
        __translation__ = "{self}.setReadCallback({callback})"

    def set_notify_callback(self, callback: callable[[], None]) -> None:
        __translation__ = "{self}.setNotifyCallback({callback})"

    # -------------------------------------------------------------------------
    # Status and configuration
    # -------------------------------------------------------------------------

    def is_connected(self) -> bool:
        """
        Check if a BLE central device is currently connected.

        Returns:
            bool: True if connected, False otherwise.
        """
        __use_as_is__ = False
        __translation__ = "{self}.isConnected()"
        return False

    def set_power(self, dbm: int) -> None:
        """
        Adjust BLE transmit power.

        Args:
            dbm (int): Power level in dBm.
        """
        __use_as_is__ = False
        __translation__ = "{self}.setPower({dbm})"

    def set_security(
        self, bonding: bool = True, mitm: bool = False, sc: bool = False
    ) -> None:
        """
        Configure BLE security and pairing parameters.

        Args:
            bonding (bool): Enable bonding (persistent pairing).
            mitm (bool): Require MITM protection.
            sc (bool): Enable LE Secure Connections.
        """
        __use_as_is__ = False
        __translation__ = "{self}.setSecurity({bonding}, {mitm}, {sc})"

    def get_address(self) -> str:
        """
        Return the ESP32’s local BLE MAC address.

        Returns:
            str: MAC address string.
        """
        __use_as_is__ = False
        __translation__ = "{self}.getAddress()"
        return "00:00:00:00:00:00"

    def is_advertising(self) -> bool:
        __translation__ = "{self}.isAdvertising()"

    def restart_advertising(self) -> None:
        __translation__ = "{self}.restartAdvertising()"

    def debug_state(self) -> None:
        __translation__ = "{self}.debugState()"
