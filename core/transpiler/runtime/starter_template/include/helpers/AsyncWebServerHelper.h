#pragma once
#include <Arduino.h>

#if defined(ESP8266)
  #include <ESPAsyncTCP.h>
  #include <ESPAsyncWebServer.h>
  #include <LittleFS.h>
  #define FS_MAIN LittleFS
  #define FS_LABEL "LittleFS"

#elif defined(ESP32)
  #include <AsyncTCP.h>
  #include <ESPAsyncWebServer.h>
  #include <SPIFFS.h>
  #define FS_MAIN SPIFFS
  #define FS_LABEL "SPIFFS"

#else
  #error "This helper supports only ESP8266 and ESP32"
#endif

// -------------------------------------------------------------------
// ✅ Universal async_server_on()
// -------------------------------------------------------------------
inline void async_server_on(
    AsyncWebServer& server,
    const String& uri_str,
    const String& method_str,
    ArRequestHandlerFunction onRequest,
    ArUploadHandlerFunction onUpload = nullptr,
    ArBodyHandlerFunction onBody = nullptr
) {
    String uri = uri_str;
    String methodUpper = method_str;
    methodUpper.toUpperCase();

    WebRequestMethodComposite method = HTTP_ANY;

    if (methodUpper == "GET") method = HTTP_GET;
    else if (methodUpper == "POST") method = HTTP_POST;
    else if (methodUpper == "PUT") method = HTTP_PUT;
    else if (methodUpper == "DELETE") method = HTTP_DELETE;
    else if (methodUpper == "PATCH") method = HTTP_PATCH;
    else if (methodUpper == "ANY") method = HTTP_ANY;

    server.on(uri.c_str(), method, onRequest, onUpload, onBody);
}

// -------------------------------------------------------------------
// ✅ Universal custom_serve_static()
// -------------------------------------------------------------------
inline AsyncStaticWebHandler& custom_serve_static(
    AsyncWebServer& server,
    const String& uri,
    const String& path,
    int cache_seconds = 3600
) {
#if defined(ESP8266)
    Serial.println("🔄 Mounting LittleFS for ESP8266...");
    if (!LittleFS.begin()) {
        Serial.println("❌ LittleFS mount failed — returning dummy handler");
        static AsyncStaticWebHandler dummy("/", LittleFS, "/", "");
        return dummy;  // can't return nullptr for a reference
    }

    Serial.println("✅ LittleFS mounted successfully");
    AsyncStaticWebHandler& handler = server.serveStatic(uri.c_str(), LittleFS, path.c_str());
    String cacheHeader = "max-age=" + String(cache_seconds);
    handler.setCacheControl(cacheHeader.c_str());
    return handler;

#elif defined(ESP32)
    Serial.println("🔄 Mounting SPIFFS for ESP32...");
    if (!SPIFFS.begin(true)) {
        Serial.println("❌ SPIFFS mount failed — returning dummy handler");
        static AsyncStaticWebHandler dummy("/", SPIFFS, "/", "");
        return dummy;
    }

    Serial.println("✅ SPIFFS mounted successfully");
    AsyncStaticWebHandler& handler = server.serveStatic(uri.c_str(), SPIFFS, path.c_str());
    String cacheHeader = "max-age=" + String(cache_seconds);
    handler.setCacheControl(cacheHeader.c_str());
    return handler;

#else
    #error "This helper supports only ESP8266 and ESP32"
#endif
}



// -------------------------------------------------------------------
// ✅ Helper: Set Cache-Control with seconds safely
// -------------------------------------------------------------------
inline AsyncStaticWebHandler& setCacheControlSeconds(AsyncStaticWebHandler& handler, int cache_seconds = 3600) {
    String cacheHeader = "max-age=" + String(cache_seconds);
    handler.setCacheControl(cacheHeader.c_str());
    Serial.printf("✅ Cache-Control set to '%s'\n", cacheHeader.c_str());
    return handler;  // Return the handler reference for chaining
}


// -------------------------------------------------------------------
// ✅ Universal async_server_on_upload()
// -------------------------------------------------------------------
// --- Upload handler Python-wrapper types ---
typedef void (*PythonUploadHandler)(
    AsyncWebServerRequest*,
    String,
    int,
    int,
    int,
    bool
);

struct UploadState {
    File file;
    int total = 0;
};

static UploadState __upload_state;

// -------------------------------------------------------------------
// INTERNAL WRAPPER — adapts real ESPAsync upload handler → python-style
// -------------------------------------------------------------------
inline void async_upload_wrapper(
    AsyncWebServerRequest *request,
    const String& filename,
    size_t index,
    uint8_t *data,
    size_t len,
    bool final,
    PythonUploadHandler py_handler
) {
    // First chunk → open file
    if (index == 0) {
        if (!FS_MAIN.begin(true)) {
            Serial.println("❌ FS mount failed in upload");
            return;
        }

        String path = "/" + filename;
        __upload_state.file = FS_MAIN.open(path, "w");
        __upload_state.total = 0;

        if (!__upload_state.file) {
            Serial.println("❌ Failed to open upload file");
            return;
        }
    }

    // Write chunk
    if (__upload_state.file) {
        __upload_state.file.write(data, len);
        __upload_state.total += len;
    }

    // Call the user's transpiled Python handler (safe types only)
    py_handler(
        request,
        filename,
        (int)index,
        (int)len,
        __upload_state.total,
        final
    );

    // Final chunk → close file
    if (final) {
        if (__upload_state.file) __upload_state.file.close();
    }
}



// -------------------------------------------------------------------
// PUBLIC HELPER: async_server_on_upload()
// This is what your stub translation calls.
// -------------------------------------------------------------------
inline void async_server_on_upload(
    AsyncWebServer& server,
    const String& uri_str,
    const String& method_str,
    PythonUploadHandler user_cb,
    ArRequestHandlerFunction final_handler = nullptr
) {
    if (!user_cb) {
        Serial.println("❌ upload callback is NULL");
        return;
    }

    // Normalize method
    String methodUpper = method_str;
    methodUpper.toUpperCase();
    WebRequestMethodComposite method = HTTP_ANY;

    if (methodUpper == "GET") method = HTTP_GET;
    else if (methodUpper == "POST") method = HTTP_POST;
    else if (methodUpper == "PUT") method = HTTP_PUT;
    else if (methodUpper == "DELETE") method = HTTP_DELETE;
    else if (methodUpper == "PATCH") method = HTTP_PATCH;

    if (!final_handler) {
        final_handler = [](AsyncWebServerRequest *request) {};
    }

    // Register route
    server.on(
        uri_str.c_str(),
        method,
        final_handler,
        [user_cb](AsyncWebServerRequest *req,
                  String filename,
                  size_t index,
                  uint8_t *data,
                  size_t len,
                  bool final)
        {
            async_upload_wrapper(req, filename, index, data, len, final, user_cb);
        }
    );
}
