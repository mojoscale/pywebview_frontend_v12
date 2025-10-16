#ifndef CUSTOM_SPIFFS_HELPER_H
#define CUSTOM_SPIFFS_HELPER_H

#include "../PyDict.h"

#ifdef ESP32
    #include <SPIFFS.h>
#elif defined(ESP8266)
    #include <FS.h>
    #include <SPIFFS.h>
#endif

PyDict<String> custom_spiffs_helper_get_spiffs_info() {
    PyDict<String> info;

#ifdef ESP32
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
    if (!SPIFFS.begin()) {
        info.set("status", "Failed to mount SPIFFS");
        return info;
    }

    FSInfo fs_info;
    SPIFFS.info(fs_info);

    info.set("status", "Mounted");
    info.set("total_bytes", String(fs_info.totalBytes));
    info.set("used_bytes", String(fs_info.usedBytes));
    info.set("free_bytes", String(fs_info.totalBytes - fs_info.usedBytes));
#endif

    return info;
}

#endif