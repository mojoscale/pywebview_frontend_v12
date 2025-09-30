#ifndef GET_LITTLEFS_INFO_ESP32_H
#define GET_LITTLEFS_INFO_ESP32_H

#if defined(ESP32)

#include <LittleFS.h>
#include "../PyDict.h"

PyDict<String> custom_littlefs_helper_get_littlefs_info() {
    PyDict<String> info;

    if (!LittleFS.begin()) {
        info.set("error", "LittleFS not mounted");
        return info;
    }

    // Use statvfs to get total and used bytes if available (esp-idf)
    // But Arduino-ESP32 LittleFS doesn't expose this. Workaround:
    File root = LittleFS.open("/");
    if (!root || !root.isDirectory()) {
        info.set("error", "Failed to open root directory");
        return info;
    }

    size_t total = 0, used = 0;

    // Estimate used space by summing file sizes
    File file = root.openNextFile();
    while (file) {
        used += file.size();
        file = root.openNextFile();
    }

    // There's no official API for total space in LittleFS (ESP32 Arduino),
    // but we can hardcode or leave it unknown
    info.set("used_bytes", String(used));
    info.set("total_bytes", "unknown");

    return info;
}


String custom_littlefs_helper_file_to_string(File file) {
    if (!file) {
        return String("[Error: File is null or failed to open]");
    }

    if (file.isDirectory()) {
        return String("[Error: Path is a directory, not a file]");
    }

    if (!file.available()) {
        return String("[Warning: File is empty or no data available]");
    }

    String output = "";
    while (file.available()) {
        output += (char)file.read();  // Reads byte-by-byte
    }

    return output;
}




#endif
#endif
