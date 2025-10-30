#ifndef ESPCAMERAHELPER_H
#define ESPCAMERAHELPER_H

#include <Arduino.h>
#include "esp_camera.h"
#include <WiFi.h>
#include <HTTPClient.h>
#include <FS.h>
#include <SPIFFS.h>

// ============================================================================
// 🧩 Helper functions for converting strings to enums
// ============================================================================
inline framesize_t string_to_framesize(const String& res) {
    if (res.equalsIgnoreCase("QQVGA"))  return FRAMESIZE_QQVGA;
    if (res.equalsIgnoreCase("QVGA"))   return FRAMESIZE_QVGA;
    if (res.equalsIgnoreCase("VGA"))    return FRAMESIZE_VGA;
    if (res.equalsIgnoreCase("SVGA"))   return FRAMESIZE_SVGA;
    if (res.equalsIgnoreCase("XGA"))    return FRAMESIZE_XGA;
    if (res.equalsIgnoreCase("SXGA"))   return FRAMESIZE_SXGA;
    if (res.equalsIgnoreCase("UXGA"))   return FRAMESIZE_UXGA;
    return FRAMESIZE_VGA;  // default fallback
}

inline pixformat_t string_to_pixformat(const String& fmt) {
    if (fmt.equalsIgnoreCase("JPEG"))      return PIXFORMAT_JPEG;
    if (fmt.equalsIgnoreCase("RGB565"))    return PIXFORMAT_RGB565;
    if (fmt.equalsIgnoreCase("YUV422"))    return PIXFORMAT_YUV422;
    if (fmt.equalsIgnoreCase("GRAYSCALE")) return PIXFORMAT_GRAYSCALE;
    return PIXFORMAT_JPEG;  // default fallback
}

// ============================================================================
// 📸 Image class - encapsulates captured frame buffer
// ============================================================================
class Image {
public:
    Image() : data(nullptr), length(0), width(0), height(0) {}
    Image(uint8_t* buf, size_t len, int w, int h)
        : data(buf), length(len), width(w), height(h) {}

    bool is_valid() const { return data != nullptr && length > 0; }

    void save(const String& path) {
        if (!SPIFFS.begin(true)) {
            Serial.println("❌ SPIFFS mount failed");
            return;
        }

        File file = SPIFFS.open(path.c_str(), FILE_WRITE);
        if (!file) {
            Serial.println("❌ Failed to open file for writing");
            return;
        }

        file.write(data, length);
        file.close();
        Serial.printf("✅ Saved %u bytes to %s\n", (unsigned int)length, path.c_str());
    }


    String base64() const {
        if (!data) return "";
        const char lookup[] =
            "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";
        String out;
        out.reserve((length * 4) / 3 + 4);
        for (size_t i = 0; i < length; i += 3) {
            uint32_t triple = (data[i] << 16)
                            | ((i + 1 < length ? data[i + 1] : 0) << 8)
                            | (i + 2 < length ? data[i + 2] : 0);
            out += lookup[(triple >> 18) & 0x3F];
            out += lookup[(triple >> 12) & 0x3F];
            out += (i + 1 < length) ? lookup[(triple >> 6) & 0x3F] : '=';
            out += (i + 2 < length) ? lookup[triple & 0x3F] : '=';
        }
        return out;
    }

    size_t size() const { return length; }
    int get_width() const { return width; }
    int get_height() const { return height; }

private:
    uint8_t* data;
    size_t length;
    int width;
    int height;

};

// ============================================================================
// 🎥 Camera class - clean C++ wrapper over esp_camera driver
// ============================================================================
class Camera {
public:
    Camera(framesize_t res = FRAMESIZE_VGA, pixformat_t fmt = PIXFORMAT_JPEG)
        : resolution(res), format(fmt), wifi_enabled(false) {}

    // ✅ Overload for string-based constructors (for transpiler)
    Camera(String res_str, String fmt_str)
    : wifi_enabled(false) {
        resolution = string_to_framesize(res_str);
        format = string_to_pixformat(fmt_str);
    }

     bool wifi_connect(const String& ssid, const String& password) {
        WiFi.begin(ssid.c_str(), password.c_str());
        Serial.printf("📡 Connecting to %s", ssid.c_str());

        int retries = 0;
        while (WiFi.status() != WL_CONNECTED && retries < 20) {
            delay(500);
            Serial.print(".");
            retries++;
        }

        if (WiFi.status() == WL_CONNECTED) {
            Serial.printf("\n✅ Wi-Fi connected, IP: %s\n",
                          WiFi.localIP().toString().c_str());
            wifi_enabled = true;
            return true;
        } else {
            Serial.println("\n❌ Wi-Fi connection failed");
            wifi_enabled = false;
            return false;
        }
    }

    // 🚦 Optional check
    bool is_wifi_connected() const {
        return WiFi.status() == WL_CONNECTED && wifi_enabled;
    }

    bool begin() {
        camera_config_t config;
        config.ledc_channel = LEDC_CHANNEL_0;
        config.ledc_timer = LEDC_TIMER_0;
        config.pin_d0 = 5;
        config.pin_d1 = 18;
        config.pin_d2 = 19;
        config.pin_d3 = 21;
        config.pin_d4 = 36;
        config.pin_d5 = 39;
        config.pin_d6 = 34;
        config.pin_d7 = 35;
        config.pin_xclk = 0;
        config.pin_pclk = 22;
        config.pin_vsync = 25;
        config.pin_href = 23;

        // ✅ Modern field names (fixes warnings)
        config.pin_sccb_sda = 26;
        config.pin_sccb_scl = 27;

        config.pin_pwdn = 32;
        config.pin_reset = -1;
        config.xclk_freq_hz = 20000000;
        config.pixel_format = format;

        if (psramFound()) {
            config.frame_size = resolution;
            config.jpeg_quality = 10;
            config.fb_count = 2;
        } else {
            config.frame_size = FRAMESIZE_CIF;
            config.jpeg_quality = 12;
            config.fb_count = 1;
        }

        esp_err_t err = esp_camera_init(&config);
        if (err != ESP_OK) {
            Serial.printf("❌ Camera init failed with error 0x%x\n", err);
            return false;
        }

        Serial.println("✅ Camera initialized");
        return true;
    }

    Image capture() {
        camera_fb_t* fb = esp_camera_fb_get();
        if (!fb) {
            Serial.println("❌ Camera capture failed");
            return Image();
        }

        Image img(fb->buf, fb->len, fb->width, fb->height);
        esp_camera_fb_return(fb);
        return img;
    }

    bool send_http(const String& urlInput) {
        String url = String(urlInput);  // Ensure safe conversion

        camera_fb_t* fb = esp_camera_fb_get();
        if (!fb) {
            Serial.println("❌ Capture failed");
            return false;
        }

        HTTPClient http;
        http.begin(url);
        http.addHeader("Content-Type", "image/jpeg");
        int code = http.POST(fb->buf, fb->len);
        esp_camera_fb_return(fb);
        http.end();

        Serial.printf("📤 HTTP POST result: %d\n", code);
        return code == 200;
    }

    void stream_http(int port = 8080) {
        WiFiServer server(port);
        server.begin();
        Serial.printf("🎥 Stream started at http://%s:%d\n",
                      WiFi.localIP().toString().c_str(), port);

        while (true) {
            WiFiClient client = server.available();
            if (!client) continue;

            client.println("HTTP/1.1 200 OK");
            client.println("Content-Type: multipart/x-mixed-replace; boundary=frame");
            client.println();

            while (client.connected()) {
                camera_fb_t* fb = esp_camera_fb_get();
                if (!fb) continue;

                client.printf("--frame\r\nContent-Type: image/jpeg\r\nContent-Length: %u\r\n\r\n", fb->len);
                client.write(fb->buf, fb->len);
                client.println();
                esp_camera_fb_return(fb);
                delay(1000 / 15);  // ~15 fps
            }
        }
    }

    void deinit() {
        esp_camera_deinit();
        Serial.println("🛑 Camera deinitialized");
    }

private:
    framesize_t resolution;
    pixformat_t format;
    bool wifi_enabled;
};

#endif
