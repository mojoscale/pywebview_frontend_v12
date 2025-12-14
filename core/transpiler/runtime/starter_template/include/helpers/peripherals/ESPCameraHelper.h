#ifndef ESPCAMERAHELPER_H
#define ESPCAMERAHELPER_H

#include <Arduino.h>
#include "esp_camera.h"
#include <WiFi.h>
#include <HTTPClient.h>
#include <FS.h>
#include <SPIFFS.h>

// ================================================================
// 🧱 Camera pin structure
// ================================================================
struct CameraPins {
    int pwdn;
    int reset;
    int xclk;
    int sda;
    int scl;
    int d7;
    int d6;
    int d5;
    int d4;
    int d3;
    int d2;
    int d1;
    int d0;
    int vsync;
    int href;
    int pclk;
};

// ================================================================
// 🔧 CENTRAL PIN DEFINITIONS (EDIT ONLY THIS SECTION)
// ================================================================

// AI Thinker ESP32-CAM
static CameraPins CAMERA_PINS_AI_THINKER = {
    32, -1, 0, 26, 27,
    35, 34, 39, 36, 21, 19, 18, 5,
    25, 23, 22
};

// Seeed Studio XIAO ESP32-S3 + camera
static CameraPins CAMERA_PINS_SEEED_XIAO = {
    -1, -1, 10, 40, 39,
    48, 47, 38, 21, 14, 13, 12, 11,
    46, 18, 17
};

// ================================================================
// 🔍 Pin lookup by name
// ================================================================
inline bool get_camera_pins(const String& name, CameraPins& out) {
    if (name.equalsIgnoreCase("AI_THINKER")) {
        out = CAMERA_PINS_AI_THINKER;
        return true;
    }
    if (name.equalsIgnoreCase("SEEED_XIAO") ||
        name.equalsIgnoreCase("SEED_XIAO") ||
        name.equalsIgnoreCase("XIAO")) {
        out = CAMERA_PINS_SEEED_XIAO;
        return true;
    }
    return false;
}

// ================================================================
// 📸 Camera class
// ================================================================
class Camera {
public:
    // ------------------------------------------------------------
    // ORIGINAL constructor (UNCHANGED)
    // ------------------------------------------------------------
    Camera(framesize_t res = FRAMESIZE_VGA,
           pixformat_t fmt = PIXFORMAT_JPEG)
        : resolution(res), format(fmt) {}

    // ------------------------------------------------------------
    // ✅ ADDED constructor (STRING-BASED)
    // NO logic change, only mapping
    // ------------------------------------------------------------
    Camera(const String& res, const String& fmt)
        : resolution(parse_framesize(res)),
          format(parse_pixformat(fmt)) {}

    // ------------------------------------------------------------
    // DEFAULT begin() → AI_THINKER
    // ------------------------------------------------------------
    bool begin() {
        return begin("AI_THINKER");
    }

    // ------------------------------------------------------------
    // begin by name
    // ------------------------------------------------------------
    bool begin(const String& variant_name) {
        CameraPins pins;
        if (!get_camera_pins(variant_name, pins)) {
            Serial.printf("❌ Unknown camera variant: %s\n",
                          variant_name.c_str());
            return false;
        }
        return begin_with_pins(pins);
    }

    // ------------------------------------------------------------
    // begin with custom pins
    // ------------------------------------------------------------
    bool begin(CameraPins& pins) {
        return begin_with_pins(pins);
    }

    // ------------------------------------------------------------
    // core init (NO logic change)
    // ------------------------------------------------------------
    bool begin_with_pins(const CameraPins& p) {
        camera_config_t config = {};
        config.ledc_channel = LEDC_CHANNEL_0;
        config.ledc_timer = LEDC_TIMER_0;

        config.pin_d0 = p.d0;
        config.pin_d1 = p.d1;
        config.pin_d2 = p.d2;
        config.pin_d3 = p.d3;
        config.pin_d4 = p.d4;
        config.pin_d5 = p.d5;
        config.pin_d6 = p.d6;
        config.pin_d7 = p.d7;

        config.pin_xclk = p.xclk;
        config.pin_pclk = p.pclk;
        config.pin_vsync = p.vsync;
        config.pin_href = p.href;
        config.pin_sccb_sda = p.sda;
        config.pin_sccb_scl = p.scl;
        config.pin_pwdn = p.pwdn;
        config.pin_reset = p.reset;

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
            Serial.printf("❌ Camera init failed (0x%x)\n", err);
            return false;
        }

        Serial.println("✅ Camera initialized");
        return true;
    }

    // ------------------------------------------------------------
    // RAW capture
    // ------------------------------------------------------------
    camera_fb_t* capture_raw_frame() {
        camera_fb_t* fb = esp_camera_fb_get();
        if (!fb) {
            Serial.println("❌ Camera capture failed");
            return nullptr;
        }
        return fb;
    }

    void release_frame(camera_fb_t* fb) {
        if (fb) esp_camera_fb_return(fb);
    }

    // ------------------------------------------------------------
    // Shutdown
    // ------------------------------------------------------------
    void deinit() {
        esp_camera_deinit();
        Serial.println("🛑 Camera deinitialized");
    }

private:
    // ------------------------------------------------------------
    // INTERNAL parsers (NO behavior change)
    // ------------------------------------------------------------
    static framesize_t parse_framesize(const String& s) {
        if (s.equalsIgnoreCase("QVGA")) return FRAMESIZE_QVGA;
        if (s.equalsIgnoreCase("VGA"))  return FRAMESIZE_VGA;
        if (s.equalsIgnoreCase("SVGA")) return FRAMESIZE_SVGA;
        if (s.equalsIgnoreCase("XGA"))  return FRAMESIZE_XGA;
        if (s.equalsIgnoreCase("SXGA")) return FRAMESIZE_SXGA;
        if (s.equalsIgnoreCase("UXGA")) return FRAMESIZE_UXGA;
        return FRAMESIZE_VGA;
    }

    static pixformat_t parse_pixformat(const String& s) {
        if (s.equalsIgnoreCase("JPEG"))   return PIXFORMAT_JPEG;
        if (s.equalsIgnoreCase("RGB565")) return PIXFORMAT_RGB565;
        if (s.equalsIgnoreCase("RGB888")) return PIXFORMAT_RGB888;
        if (s.equalsIgnoreCase("GRAYSCALE")) return PIXFORMAT_GRAYSCALE;
        return PIXFORMAT_JPEG;
    }

private:
    framesize_t resolution;
    pixformat_t format;
};

#endif
