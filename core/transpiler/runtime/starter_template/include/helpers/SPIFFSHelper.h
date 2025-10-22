#ifndef CUSTOM_SPIFFS_HELPER_H
#define CUSTOM_SPIFFS_HELPER_H
#include "../PyDict.h"

#ifdef ESP32
    #include <SPIFFS.h>
#elif defined(ESP8266)
    #include <FS.h>
    // Don't redefine SPIFFS; use the global SPIFFS object directly
#endif

/**
 * Generic helper to get total SPIFFS bytes (works on both ESP32 and ESP8266)
 */
size_t custom_spiffs_helper_get_total_bytes() {
#ifdef ESP32
    return SPIFFS.totalBytes();
#elif defined(ESP8266)
    FSInfo fs_info;
    SPIFFS.info(fs_info);
    return fs_info.totalBytes;
#endif
}

/**
 * Generic helper to get used SPIFFS bytes (works on both ESP32 and ESP8266)
 * ESP8266 doesn't have usedBytes() so we iterate through files to calculate it
 */
size_t custom_spiffs_helper_get_used_bytes() {
#ifdef ESP32
    return SPIFFS.usedBytes();
#elif defined(ESP8266)
    size_t used = 0;
    Dir dir = SPIFFS.openDir("/");
    
    while (dir.next()) {
        File file = dir.openFile("r");
        used += file.size();
        file.close();
    }
    
    return used;
#endif
}

PyDict<String> custom_spiffs_helper_get_spiffs_info() {
    PyDict<String> info;

#ifdef ESP32
    // ESP32: SPIFFS API
    if (!SPIFFS.begin(true)) {
        info.set("status", "Failed to mount SPIFFS");
        return info;
    }
    size_t total = SPIFFS.totalBytes();
    size_t used = SPIFFS.usedBytes();
    info.set("status", "Mounted");
    info.set("total_bytes", String(total));
    info.set("used_bytes", String(used));
    info.set("free_bytes", String(total - used));
    
#elif defined(ESP8266)
    // ESP8266: SPIFFS API (via FS.h)
    if (!SPIFFS.begin()) {
        info.set("status", "Failed to mount SPIFFS");
        return info;
    }
    
    // Use generic helper functions (work on both ESP32 and ESP8266)
    size_t total = custom_spiffs_helper_get_total_bytes();
    size_t used = custom_spiffs_helper_get_used_bytes();
    
    info.set("status", "Mounted");
    info.set("total_bytes", String(total));
    info.set("used_bytes", String(used));
    info.set("free_bytes", String(total - used));
#endif

    return info;
}

#endif