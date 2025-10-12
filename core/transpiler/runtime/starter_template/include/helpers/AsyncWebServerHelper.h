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
inline AsyncStaticWebHandler* custom_serve_static(
    AsyncWebServer& server,
    const String& uri,
    const String& path,
    int cache_seconds = 3600
) {
#if defined(ESP8266)
    Serial.println("🔄 Mounting LittleFS for ESP8266...");
    if (!LittleFS.begin()) {
        Serial.println("❌ LittleFS mount failed");
        return nullptr;
    }

    Serial.println("✅ LittleFS mounted successfully");
    auto* handler = &server.serveStatic(uri.c_str(), LittleFS, path.c_str());
    String cacheHeader = "max-age=" + String(cache_seconds);
    handler->setCacheControl(cacheHeader.c_str());
    return handler;

#elif defined(ESP32)
    Serial.println("🔄 Mounting SPIFFS for ESP32...");
    if (!SPIFFS.begin(true)) {
        Serial.println("❌ SPIFFS mount failed");
        return nullptr;
    }

    Serial.println("✅ SPIFFS mounted successfully");
    auto* handler = &server.serveStatic(uri.c_str(), SPIFFS, path.c_str());
    String cacheHeader = "max-age=" + String(cache_seconds);
    handler->setCacheControl(cacheHeader.c_str());
    return handler;
#endif
}

// -------------------------------------------------------------------
// ✅ Helper: Set Cache-Control with seconds safely
// -------------------------------------------------------------------
inline void setCacheControlSeconds(AsyncStaticWebHandler* handler, int cache_seconds = 3600) {
    if (!handler) {
        Serial.println("⚠️ setCacheControlSeconds: null handler pointer");
        return;
    }

    String cacheHeader = "max-age=" + String(cache_seconds);
    handler->setCacheControl(cacheHeader.c_str());
    Serial.printf("✅ Cache-Control set to '%s'\n", cacheHeader.c_str());
}
