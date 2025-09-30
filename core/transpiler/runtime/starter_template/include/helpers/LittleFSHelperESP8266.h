#ifndef GET_LITTLEFS_INFO_ESP8266_H
#define GET_LITTLEFS_INFO_ESP8266_H

#if defined(ESP8266)

#include <LittleFS.h>
#include "../PyDict.h"

PyDict<String> custom_littlefs_helper_get_littlefs_info() {
    PyDict<String> info;

    FSInfo fs_info;
    if (LittleFS.info(fs_info)) {
        info.set("total_bytes", String(fs_info.totalBytes));
        info.set("used_bytes", String(fs_info.usedBytes));
        info.set("block_size", String(fs_info.blockSize));
        info.set("page_size", String(fs_info.pageSize));
        info.set("max_open_files", String(fs_info.maxOpenFiles));
        info.set("max_path_length", String(fs_info.maxPathLength));
    } else {
        info.set("error", "Failed to get FS info");
    }

    return info;
}

String custom_littlefs_helper_file_to_string(File file) {
    if (!file || file.isDirectory()) {
        return String("[Invalid or directory]");
    }

    String output = "";
    while (file.available()) {
        output += (char)file.read();  // Reads byte-by-byte
    }
    return output;
}

#endif
#endif
