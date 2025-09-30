#include <WiFiManager.h>  // Make sure this is already included

bool custom_wifi_manager_helper_start_wifi_portal(WiFiManager& manager, const String& ssid, const String& password) {
    // Convert String to const char* (needed for WiFiManager)
    const char* ap_ssid = ssid.c_str();
    const char* ap_password = password.c_str();

    return manager.startConfigPortal(ap_ssid, ap_password);
}


bool custom_wifi_manager_helper_auto_connect(WiFiManager& manager, const String& ssid, const String& password) {
    // Convert String to const char* for compatibility
    const char* ap_ssid = ssid.c_str();
    const char* ap_password = password.c_str();

    return manager.autoConnect(ap_ssid, ap_password);
}
