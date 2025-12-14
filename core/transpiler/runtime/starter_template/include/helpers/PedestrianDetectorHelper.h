#pragma once

#include <Arduino.h>
#include <list>

#include "esp_camera.h"
#include "dl_image.hpp"
#include "dl_image_jpeg.hpp"
#include "pedestrian_detect.hpp"

#if CONFIG_PEDESTRIAN_DETECT_MODEL_IN_SDCARD
#include "bsp/esp-bsp.h"
#endif

class PedestrianDetector {
private:
    PedestrianDetect* detector = nullptr;
    bool ready = false;

public:
    // ============================================================
    // Init
    // ============================================================
    bool begin() {
#if CONFIG_PEDESTRIAN_DETECT_MODEL_IN_SDCARD
        if (bsp_sdcard_mount() != ESP_OK) {
            Serial.println("❌ SD card mount failed");
            return false;
        }
#endif
        detector = new PedestrianDetect();
        ready = (detector != nullptr);
        return ready;
    }

    bool is_ready() const {
        return ready;
    }

    // ============================================================
    // SIMPLE detection (THIS WAS MISSING)
    // ============================================================
    bool detect(camera_fb_t* fb) {
        if (!ready || !fb || !fb->buf) {
            return false;
        }

        dl::image::img_t img{};

        if (fb->format == PIXFORMAT_JPEG) {
            dl::image::jpeg_img_t jpeg{
                .data = fb->buf,
                .data_len = fb->len
            };

            img = dl::image::sw_decode_jpeg(
                jpeg,
                dl::image::DL_IMAGE_PIX_TYPE_RGB888
            );

            if (!img.data) {
                return false;
            }
        } else {
            img.data = fb->buf;
            img.width = fb->width;
            img.height = fb->height;
            img.pix_type = dl::image::DL_IMAGE_PIX_TYPE_RGB888;
        }

        auto& results = detector->run(img);

        if (fb->format == PIXFORMAT_JPEG && img.data) {
            heap_caps_free(img.data);
        }

        return !results.empty();
    }

    // ============================================================
    // FULL detection → PyDict<String>
    // ============================================================
    PyDict<String> detect_full(camera_fb_t* fb) {
        PyDict<String> out;

        if (!ready || !fb || !fb->buf) {
            return out;
        }

        dl::image::img_t img{};

        if (fb->format == PIXFORMAT_JPEG) {
            dl::image::jpeg_img_t jpeg{
                .data = fb->buf,
                .data_len = fb->len
            };

            img = dl::image::sw_decode_jpeg(
                jpeg,
                dl::image::DL_IMAGE_PIX_TYPE_RGB888
            );

            if (!img.data) {
                return out;
            }
        } else {
            img.data = fb->buf;
            img.width = fb->width;
            img.height = fb->height;
            img.pix_type = dl::image::DL_IMAGE_PIX_TYPE_RGB888;
        }

        auto& results = detector->run(img);

        out.set("count", String(results.size()));

        int i = 0;
        for (const auto& r : results) {
            out.set("det" + String(i) + "_score", String(r.score, 4));
            out.set("det" + String(i) + "_x1", String(r.box[0]));
            out.set("det" + String(i) + "_y1", String(r.box[1]));
            out.set("det" + String(i) + "_x2", String(r.box[2]));
            out.set("det" + String(i) + "_y2", String(r.box[3]));
            ++i;
        }

        if (fb->format == PIXFORMAT_JPEG && img.data) {
            heap_caps_free(img.data);
        }

        return out;
    }

    // ============================================================
    // RAW detection (list<result_t>)
    // ============================================================
    bool detect_raw(
        camera_fb_t* fb,
        std::list<dl::detect::result_t>& results
    ) {
        results.clear();

        if (!ready || !fb || !fb->buf) {
            return false;
        }

        dl::image::img_t img{};

        if (fb->format == PIXFORMAT_JPEG) {
            dl::image::jpeg_img_t jpeg{
                .data = fb->buf,
                .data_len = fb->len
            };

            img = dl::image::sw_decode_jpeg(
                jpeg,
                dl::image::DL_IMAGE_PIX_TYPE_RGB888
            );

            if (!img.data) {
                return false;
            }
        } else {
            img.data = fb->buf;
            img.width = fb->width;
            img.height = fb->height;
            img.pix_type = dl::image::DL_IMAGE_PIX_TYPE_RGB888;
        }

        results = detector->run(img);

        if (fb->format == PIXFORMAT_JPEG && img.data) {
            heap_caps_free(img.data);
        }

        return true;
    }

    // ============================================================
    // Cleanup
    // ============================================================
    void end() {
        if (detector) {
            delete detector;
            detector = nullptr;
        }
        ready = false;
    }
};
