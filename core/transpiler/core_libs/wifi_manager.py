

__include_modules__ = "WiFiManager"
__dependencies__ = "tzapu/WiFiManager"

__include_internal_modules__ = "helpers/WiFiManagerHelper"



class WiFiManager:
    """
    A WiFi manager that auto-connects to known networks or opens a config portal for ESP32/ESP8266.
    """

    def __init__(self) -> None:
        __translation__ = ""
        __class_actual_type__ = "WiFiManager"


    def setDebugOutput(self, enable: bool) -> None:
        """
        Enable or disable debug logging on Serial.
        """
        __use_as_is__ = True
        pass

    def resetSettings(self) -> None:
        """
        Clear stored WiFi credentials from flash.
        """
        __use_as_is__ = True
        pass

    def autoConnect(self, ap_name: str, ap_password: str) -> bool:
        """
        Connect to saved WiFi or start a config portal.

        Args:
            ap_name (str): The SSID for the access point in config mode.
            ap_password (str): Password for the access point.

        Returns:
            bool: True if WiFi connection was successful.
        """
        __use_as_is__ = False
        __translation__ = "custom_wifi_manager_helper_auto_connect({0}, {1}, {2})"
        return False

    def startConfigPortal(self, ap_name: str, ap_password: str) -> bool:
        """
        Force start the configuration portal regardless of existing WiFi credentials.

        Args:
            ap_name (str): The SSID for the access point.
            ap_password (str): Password for the access point.

        Returns:
            bool: True if WiFi connected successfully.
        """
        __use_as_is__ = False
        __translation__ = "custom_wifi_manager_helper_start_wifi_portal({0}, {1}, {2})"
        return False

    def setTimeout(self, seconds: int) -> None:
        """
        Set timeout for config portal to auto-exit if no connection is made.
        """
        __use_as_is__ = True
        pass

    def setConnectTimeout(self, seconds: int) -> None:
        """
        Set timeout for how long to wait for WiFi connection before failing.
        """
        pass

    def setMinimumSignalQuality(self, quality: int) -> None:
        """
        Only show WiFi networks above this signal quality (in percent).
        """

        __use_as_is__ = True
        pass
