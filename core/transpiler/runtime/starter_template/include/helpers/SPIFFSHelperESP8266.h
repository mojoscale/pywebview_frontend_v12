#ifdef ESP8266

#include <FS.h>
#include <SPIFFS.h>
#include "../PyDict.h"

PyDict<String> custom_spiffs_helper_get_spiffs_info() {
    PyDict<String> info;

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

    return info;
}

#endif
