#include <WiFi.h>  // For ESP32; use <ESP8266WiFi.h> for ESP8266
#include "../PyList.h"

// Scans for available WiFi networks and returns them as PyList<String>
PyList<String> custom_wifi_helper_scan_wifi_networks() {
    PyList<String> ssid_list;

    Serial.println("🔍 Scanning for WiFi networks...");
    int n = WiFi.scanNetworks();

    if (n == 0) {
        Serial.println("⚠️  No networks found.");
        return ssid_list;  // return empty list
    }

    for (int i = 0; i < n; ++i) {
        String ssid = WiFi.SSID(i);
        ssid_list.append(ssid);
    }

    Serial.print("✅ Found ");
    Serial.print(n);
    Serial.println(" networks.");
    return ssid_list;
}

// ---- connect(String host, int port) ----
bool custom_wifi_client_helper_connect(WiFiClient& client, const String& host, int port) {
    const char* host_cstr = host.c_str();
    return client.connect(host_cstr, port);
}

// ---- write(String data) ----
int custom_wifi_client_helper_write(WiFiClient& client, const String& data) {
    const char* data_cstr = data.c_str();
    return client.write((const uint8_t*)data_cstr, strlen(data_cstr));
}

// ---- print(String data) ----
int custom_wifi_client_helper_print(WiFiClient& client, const String& data) {
    return client.print(data);
}

// ---- println(String data) ----
int custom_wifi_client_helper_println(WiFiClient& client, const String& data) {
    return client.println(data);
}

int custom_wifi_client_helper_readBytes(WiFiClient& client, const String& buffer_string, int length) {
    char* buffer = new char[length + 1];  // +1 for null terminator (safe)
    buffer_string.toCharArray(buffer, length + 1);

    int bytes_read = client.readBytes(buffer, length);

    // Optional: you can do something with buffer here

    delete[] buffer;  // prevent memory leak
    return bytes_read;
}

String custom_wifi_helper_local_ip_to_string() {
    IPAddress ip = WiFi.localIP();
    char buf[16];
    sprintf(buf, "%u.%u.%u.%u", ip[0], ip[1], ip[2], ip[3]);
    return String(buf);
}



