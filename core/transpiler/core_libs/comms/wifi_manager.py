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

    def set_debug_output(self, enable: bool) -> None:
        """
        Enable or disable debug logging on Serial.
        """
        __use_as_is__ = True
        __translation__ = "{self}.setDebugOutput({enable})"
        pass

    def reset_settings(self) -> None:
        """
        Clear stored WiFi credentials from flash.
        """
        __use_as_is__ = True
        __translation__ = "{self}.resetSettings()"
        pass

    def auto_connect(self, ap_name: str, ap_password: str) -> bool:
        """
        Connect to saved WiFi or start a config portal.

        Args:
            ap_name (str): The SSID for the access point in config mode.
            ap_password (str): Password for the access point.

        Returns:
            bool: True if WiFi connection was successful.
        """
        __use_as_is__ = False
        __translation__ = (
            "custom_wifi_manager_helper_auto_connect({self}, {ap_name}, {ap_password})"
        )
        return False

    def start_config_portal(self, ap_name: str, ap_password: str) -> bool:
        """
        Force start the configuration portal regardless of existing WiFi credentials.

        Args:
            ap_name (str): The SSID for the access point.
            ap_password (str): Password for the access point.

        Returns:
            bool: True if WiFi connected successfully.
        """
        __use_as_is__ = False
        __translation__ = "custom_wifi_manager_helper_start_wifi_portal({self}, {ap_name}, {ap_password})"
        return False

    def set_timeout(self, seconds: int) -> None:
        """
        Set timeout for config portal to auto-exit if no connection is made.
        """
        __use_as_is__ = True
        __translation__ = "{self}.setTimeout({seconds})"
        pass

    def set_connect_timeout(self, seconds: int) -> None:
        """
        Set timeout for how long to wait for WiFi connection before failing.
        """
        __translation__ = "{self}.setConnectTimeout({seconds})"

    def set_minimum_signal_quality(self, quality: int) -> None:
        """
        Only show WiFi networks above this signal quality (in percent).
        """

        __use_as_is__ = True
        __translation__ = "{self}.setMinimumSignalQuality({quality})"
        pass
