#pragma once
#include <Arduino.h>
#include <SPIFFS.h>
#include <math.h>

// Basic ESP-DL includes
#include "dl_detect_base.hpp"
#include "dl_detect_pico_postprocessor.hpp"
#include "dl_image.hpp"

// Include your ESPCameraHelper to get the Image class
#include "helpers/peripherals/ESPCameraHelper.h"

#define PEDESTRIAN_MODEL_PATH "/spiffs/pedestrian_detector.espdl"

class PedestrianDetector {
private:
    bool model_loaded;
    dl::Model* model;
    dl::image::ImagePreprocessor* image_preprocessor;
    dl::detect::PicoPostprocessor* postprocessor;
    float score_threshold;
    float nms_threshold;
    
public:
    PedestrianDetector(float score_thr = 0.7f, float nms_thr = 0.5f) : 
        model_loaded(false), model(nullptr), image_preprocessor(nullptr), 
        postprocessor(nullptr), score_threshold(score_thr), nms_threshold(nms_thr) {}

    ~PedestrianDetector() {
        if (postprocessor) delete postprocessor;
        if (image_preprocessor) delete image_preprocessor;
        if (model) delete model;
    }

    bool begin() {
        Serial.println("[PedestrianDetector] Initializing from SPIFFS...");
        
        if (!SPIFFS.begin(true)) {
            Serial.println("❌ SPIFFS mount failed");
            return false;
        }

        if (!load_model_from_spiffs()) {
            Serial.println("❌ Model load from SPIFFS failed");
            return false;
        }

        model_loaded = true;
        Serial.println("✅ PedestrianDetector ready");
        return true;
    }

    // Main detection method that takes your Image class
    bool detect(Image& image) {
        if (!model_loaded || !model) {
            Serial.println("❌ Model not loaded");
            return false;
        }

        if (!image.is_valid()) {
            Serial.println("❌ Invalid image");
            return false;
        }

        Serial.printf("🖼️ Processing image: %dx%d, size: %d bytes\n", 
                     image.get_width(), image.get_height(), image.size());

        // Use simple image analysis as placeholder
        bool detected = analyze_image_simple(image);
        Serial.printf("🎯 Detection result: %s\n", detected ? "PEDESTRIAN" : "NO PEDESTRIAN");
        return detected;
    }

    // Overload for camera_fb_t (convenience method)
    bool detect(camera_fb_t* frame) {
        if (!frame || !frame->buf) {
            Serial.println("❌ Invalid camera frame");
            return false;
        }
        
        Image image(frame->buf, frame->len, frame->width, frame->height);
        return detect(image);
    }

    bool isReady() const { 
        return model_loaded; 
    }

    void setThreshold(float score_thr, float nms_thr = 0.5f) { 
        score_threshold = score_thr;
        nms_threshold = nms_thr;
    }

private:
    bool load_model_from_spiffs() {
        if (!SPIFFS.exists(PEDESTRIAN_MODEL_PATH)) {
            Serial.printf("❌ Model file not found: %s\n", PEDESTRIAN_MODEL_PATH);
            return false;
        }

        File file = SPIFFS.open(PEDESTRIAN_MODEL_PATH, "r");
        if (!file) {
            Serial.println("❌ Failed to open model file");
            return false;
        }

        size_t model_size = file.size();
        uint8_t* model_data = (uint8_t*)heap_caps_malloc(model_size, MALLOC_CAP_8BIT | MALLOC_CAP_SPIRAM);
        
        if (!model_data) {
            Serial.println("❌ Failed to allocate memory for model");
            file.close();
            return false;
        }

        file.read(model_data, model_size);
        file.close();

        Serial.printf("📦 Model loaded from SPIFFS: %d bytes\n", model_size);

        // Remove try-catch - use simple error checking instead
        model = new dl::Model((const char*)model_data, "pedestrian_detector");
        
        heap_caps_free(model_data);

        if (!model) {
            Serial.println("❌ Failed to create model");
            return false;
        }

        // Initialize like the ESP-DL example
        model->minimize();
        
        #if CONFIG_IDF_TARGET_ESP32P4
        image_preprocessor = new dl::image::ImagePreprocessor(model, {0, 0, 0}, {1, 1, 1});
        #else
        image_preprocessor = new dl::image::ImagePreprocessor(
            model, {0, 0, 0}, {1, 1, 1}, dl::image::DL_IMAGE_CAP_RGB565_BIG_ENDIAN);
        #endif

        if (!image_preprocessor) {
            Serial.println("❌ Failed to create image preprocessor");
            delete model;
            model = nullptr;
            return false;
        }

        postprocessor = new dl::detect::PicoPostprocessor(
            model, image_preprocessor, score_threshold, nms_threshold, 10, 
            {{8, 8, 4, 4}, {16, 16, 8, 8}, {32, 32, 16, 16}});

        if (!postprocessor) {
            Serial.println("❌ Failed to create postprocessor");
            delete image_preprocessor;
            delete model;
            model = nullptr;
            image_preprocessor = nullptr;
            return false;
        }

        return true;
    }

    bool analyze_image_simple(Image& image) {
        // Simple image analysis as placeholder
        // Replace this with actual ESP-DL inference when ready
        
        const uint8_t* img_data = image.get_data();
        int width = image.get_width();
        int height = image.get_height();
        
        if (!img_data || width <= 0 || height <= 0) {
            return false;
        }

        // Calculate average brightness
        long sum = 0;
        int total_pixels = width * height;
        
        // Simple sampling to avoid processing every pixel
        int step = (total_pixels > 1000) ? total_pixels / 1000 : 1;
        int sampled_pixels = 0;
        
        for (int i = 0; i < total_pixels; i += step) {
            sum += img_data[i];
            sampled_pixels++;
        }
        
        float avg_brightness = sum / (float)sampled_pixels;
        
        // Simple heuristic for pedestrian detection simulation
        // This alternates detection to test the pipeline
        static unsigned long last_detection = 0;
        static bool last_result = false;
        
        // Change detection every 5 seconds for testing
        if (millis() - last_detection > 5000) {
            last_detection = millis();
            last_result = !last_result; // Alternate between true/false
        }
        
        Serial.printf("🔍 Image analysis: brightness=%.1f, simulated=%s\n", 
                     avg_brightness, last_result ? "DETECTED" : "NOT_DETECTED");
        
        return last_result;
    }
};