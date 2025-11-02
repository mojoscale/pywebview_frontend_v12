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
    return FRAMESIZE_VGA;
}

inline pixformat_t string_to_pixformat(const String& fmt) {
    if (fmt.equalsIgnoreCase("JPEG"))      return PIXFORMAT_JPEG;
    if (fmt.equalsIgnoreCase("RGB565"))    return PIXFORMAT_RGB565;
    if (fmt.equalsIgnoreCase("YUV422"))    return PIXFORMAT_YUV422;
    if (fmt.equalsIgnoreCase("GRAYSCALE")) return PIXFORMAT_GRAYSCALE;
    return PIXFORMAT_JPEG;
}

// ============================================================================
// 🧱 Variant Structs
// ============================================================================
struct CameraPins {
    int pin_pwdn;
    int pin_reset;
    int pin_xclk;
    int pin_sscb_sda;
    int pin_sscb_scl;
    int pin_d7;
    int pin_d6;
    int pin_d5;
    int pin_d4;
    int pin_d3;
    int pin_d2;
    int pin_d1;
    int pin_d0;
    int pin_vsync;
    int pin_href;
    int pin_pclk;
};

// Common camera modules
static const CameraPins CAMERA_VARIANT_AI_THINKER = {
    .pin_pwdn = 32,
    .pin_reset = -1,
    .pin_xclk = 0,
    .pin_sscb_sda = 26,
    .pin_sscb_scl = 27,
    .pin_d7 = 35,
    .pin_d6 = 34,
    .pin_d5 = 39,
    .pin_d4 = 36,
    .pin_d3 = 21,
    .pin_d2 = 19,
    .pin_d1 = 18,
    .pin_d0 = 5,
    .pin_vsync = 25,
    .pin_href = 23,
    .pin_pclk = 22
};

static const CameraPins CAMERA_VARIANT_WROVER = {
    .pin_pwdn = -1,
    .pin_reset = -1,
    .pin_xclk = 21,
    .pin_sscb_sda = 26,
    .pin_sscb_scl = 27,
    .pin_d7 = 35,
    .pin_d6 = 34,
    .pin_d5 = 39,
    .pin_d4 = 36,
    .pin_d3 = 19,
    .pin_d2 = 18,
    .pin_d1 = 5,
    .pin_d0 = 4,
    .pin_vsync = 25,
    .pin_href = 23,
    .pin_pclk = 22
};

static const CameraPins CAMERA_VARIANT_M5STACK = {
    .pin_pwdn = -1,
    .pin_reset = 15,
    .pin_xclk = 27,
    .pin_sscb_sda = 25,
    .pin_sscb_scl = 23,
    .pin_d7 = 19,
    .pin_d6 = 36,
    .pin_d5 = 18,
    .pin_d4 = 39,
    .pin_d3 = 5,
    .pin_d2 = 34,
    .pin_d1 = 35,
    .pin_d0 = 32,
    .pin_vsync = 22,
    .pin_href = 26,
    .pin_pclk = 21
};

// ============================================================================
// 📸 Image class
// ============================================================================
class Image {
public:
    Image() : data(nullptr), length(0), width(0), height(0) {}
    Image(uint8_t* buf, size_t len, int w, int h)
        : data(buf), length(len), width(w), height(h) {}

    bool is_valid() const { return data && length > 0; }

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

    // ✅ restore the missing getters
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
// 🎥 Camera class
// ============================================================================
class Camera {
public:
    Camera(framesize_t res = FRAMESIZE_VGA, pixformat_t fmt = PIXFORMAT_JPEG)
        : resolution(res), format(fmt), wifi_enabled(false) {}

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
            Serial.printf("\n✅ Wi-Fi connected, IP: %s\n", WiFi.localIP().toString().c_str());
            wifi_enabled = true;
            return true;
        } else {
            Serial.println("\n❌ Wi-Fi connection failed");
            wifi_enabled = false;
            return false;
        }
    }

    bool is_wifi_connected() const {
        return WiFi.status() == WL_CONNECTED && wifi_enabled;
    }

    // ============================================================================
    // ✅ Variant-based begin()
    // ============================================================================
    bool begin(const String& variant_name) {
        CameraPins pins;

        if (variant_name.equalsIgnoreCase("AI_THINKER")) {
            pins = CAMERA_VARIANT_AI_THINKER;
        } else if (variant_name.equalsIgnoreCase("WROVER")) {
            pins = CAMERA_VARIANT_WROVER;
        } else if (variant_name.equalsIgnoreCase("M5STACK")) {
            pins = CAMERA_VARIANT_M5STACK;
        } else {
            Serial.printf("⚠️ Unknown camera variant '%s', defaulting to AI_THINKER\n", variant_name.c_str());
            pins = CAMERA_VARIANT_AI_THINKER;
        }

        return begin_custom(
            pins.pin_pwdn, pins.pin_reset, pins.pin_xclk,
            pins.pin_sscb_sda, pins.pin_sscb_scl,
            pins.pin_d7, pins.pin_d6, pins.pin_d5, pins.pin_d4,
            pins.pin_d3, pins.pin_d2, pins.pin_d1, pins.pin_d0,
            pins.pin_vsync, pins.pin_href, pins.pin_pclk
        );
    }

    // ============================================================================
    // 🧩 Custom begin() with detailed pins
    // ============================================================================
    bool begin_custom(
        int pin_pwdn, int pin_reset, int pin_xclk,
        int pin_sscb_sda, int pin_sscb_scl,
        int pin_d7, int pin_d6, int pin_d5, int pin_d4,
        int pin_d3, int pin_d2, int pin_d1, int pin_d0,
        int pin_vsync, int pin_href, int pin_pclk
    ) {
        camera_config_t config;
        config.ledc_channel = LEDC_CHANNEL_0;
        config.ledc_timer = LEDC_TIMER_0;
        config.pin_d0 = pin_d0;
        config.pin_d1 = pin_d1;
        config.pin_d2 = pin_d2;
        config.pin_d3 = pin_d3;
        config.pin_d4 = pin_d4;
        config.pin_d5 = pin_d5;
        config.pin_d6 = pin_d6;
        config.pin_d7 = pin_d7;
        config.pin_xclk = pin_xclk;
        config.pin_pclk = pin_pclk;
        config.pin_vsync = pin_vsync;
        config.pin_href = pin_href;
        config.pin_sccb_sda = pin_sscb_sda;
        config.pin_sccb_scl = pin_sscb_scl;
        config.pin_pwdn = pin_pwdn;
        config.pin_reset = pin_reset;
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
            Serial.printf("❌ Camera init failed (err=0x%x)\n", err);
            return false;
        }

        Serial.println("✅ Camera initialized");
        return true;
    }

    // ============================================================================
    // 🖼️ Capture
    // ============================================================================
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

    bool send_http(const String& url) {
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
                delay(1000 / 15);  // 15 FPS approx
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
