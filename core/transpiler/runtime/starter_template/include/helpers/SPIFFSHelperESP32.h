#ifdef ESP32

#include <SPIFFS.h>
#include "../PyDict.h"

PyDict<String> custom_spiffs_helper_get_spiffs_info() {
    PyDict<String> info;

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

    return info;
}

#endif
