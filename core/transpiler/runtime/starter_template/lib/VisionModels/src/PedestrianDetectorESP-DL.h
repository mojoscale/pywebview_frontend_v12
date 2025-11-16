#pragma once
#include <Arduino.h>
#include "dl_tool.hpp"        // Main ESP-DL tool header
#include "nn.hpp"             // Neural network operations
#include "layer.hpp"          // Layer definitions
#include "model.hpp"          // Model definitions
#include "tensor.hpp"         // Tensor operations
#include "esp_dl_define.hpp"  // ESP-DL definitions
#include <esp_heap_caps.h>    // For memory allocation
#include "helpers/peripherals/ESPCameraHelper.h"

using namespace dl;
using namespace nn;

// Path to model in storage
#define PEDESTRIAN_DETECTOR_MODEL_PATH "/pedestrian_detector.espdl"
#define PEDESTRIAN_DETECTOR_INPUT_W 96
#define PEDESTRIAN_DETECTOR_INPUT_H 96
#define PEDESTRIAN_DETECTOR_INPUT_C 1
#define PEDESTRIAN_DETECTOR_NUM_CLASSES 2

class PedestrianDetector {
public:
    PedestrianDetector() :
        threshold(0.6f),
        ready(false),
        input_tensor(nullptr) {}

    ~PedestrianDetector() {
        cleanup();
    }

    bool begin() {
        Serial.println("🔄 Initializing ESP-DL PedestrianDetector...");

        // Allocate input tensor (1, 96, 96, 1) - NHWC format
        try {
            input_tensor = new Tensor<int16_t>({1, PEDESTRIAN_DETECTOR_INPUT_H, 
                                               PEDESTRIAN_DETECTOR_INPUT_W, 
                                               PEDESTRIAN_DETECTOR_INPUT_C});
        } catch (const std::exception& e) {
            Serial.println("❌ Failed to allocate input tensor");
            return false;
        }

        if (!input_tensor) {
            Serial.println("❌ Failed to allocate input tensor");
            return false;
        }

        // Load model from storage
        if (!loadModelFromFS()) {
            Serial.println("❌ Model loading failed");
            return false;
        }

        ready = true;
        Serial.println("✅ PedestrianDetector ready (ESP-DL)");
        return true;
    }

    bool detect(const Image& img) {
        if (!ready) {
            Serial.println("❌ Model not initialized");
            return false;
        }
        if (!img.is_valid()) {
            Serial.println("❌ Invalid image");
            return false;
        }

        if (!prepare_input(img)) {
            Serial.println("❌ Failed processing image");
            return false;
        }

        // Run inference
        Tensor<int16_t>* output = run_inference();
        
        if (!output) {
            Serial.println("❌ Inference failed");
            return false;
        }

        // Assuming output is [1, 2] tensor with [no_person, yes_person] scores
        // Convert int16_t to float for scoring
        float no_person = output->get_element(0, 0) / 32767.0f;
        float yes_person = output->get_element(0, 1) / 32767.0f;

        Serial.printf("[PedestrianDetector ESP-DL] Scores: [no=%.3f, yes=%.3f]\n",
                      no_person, yes_person);

        // Clean up output tensor
        delete output;

        return yes_person >= threshold;
    }

    void setThreshold(float new_threshold) {
        threshold = new_threshold;
    }

    bool isReady() const {
        return ready;
    }

private:
    float threshold;
    bool ready;
    Tensor<int16_t>* input_tensor;
    // Add your model instance here based on your specific model type
    // Example: YourModelClass* model;

    void cleanup() {
        if (input_tensor) {
            delete input_tensor;
            input_tensor = nullptr;
        }
        // Clean up model if needed
        // if (model) { delete model; model = nullptr; }
    }

    bool loadModelFromFS() {
        if (!SPIFFS.exists(PEDESTRIAN_DETECTOR_MODEL_PATH)) {
            Serial.printf("❌ Model file not found: %s\n", PEDESTRIAN_DETECTOR_MODEL_PATH);
            return false;
        }

        File f = SPIFFS.open(PEDESTRIAN_DETECTOR_MODEL_PATH, "r");
        if (!f) {
            Serial.printf("❌ Cannot open model file: %s\n", PEDESTRIAN_DETECTOR_MODEL_PATH);
            return false;
        }

        size_t size = f.size();
        uint8_t* buffer = (uint8_t*) malloc(size);

        if (!buffer) {
            Serial.println("❌ malloc failed for model buffer");
            f.close();
            return false;
        }

        f.read(buffer, size);
        f.close();

        // TODO: Load your specific model format here
        // This depends on how your pedestrian_detector.espdl model is structured
        // Example:
        // model = new YourModelClass();
        // bool success = model->load_from_buffer(buffer, size);
        
        Serial.printf("📦 Model loaded from storage, size: %d bytes\n", size);
        
        // Free buffer after loading (unless your model keeps it)
        free(buffer);
        
        return true; // Change this based on actual model loading success
    }

    Tensor<int16_t>* run_inference() {
        if (!input_tensor) {
            return nullptr;
        }

        // TODO: Replace with your actual model inference
        // This is a placeholder - you need to implement based on your specific model
        try {
            Tensor<int16_t>* output = new Tensor<int16_t>({1, PEDESTRIAN_DETECTOR_NUM_CLASSES});
            
            if (!output) {
                return nullptr;
            }

            // Placeholder inference - replace with actual model call
            // Example: model->forward(*input_tensor, *output);
            
            // Generate placeholder scores
            for (int i = 0; i < PEDESTRIAN_DETECTOR_NUM_CLASSES; i++) {
                output->set_element(static_cast<int16_t>(random(1000) - 500), 0, i);
            }
            
            return output;
        } catch (const std::exception& e) {
            Serial.printf("Inference error: %s\n", e.what());
            return nullptr;
        }
    }

    bool prepare_input(const Image& img) {
        if (!input_tensor) return false;

        const uint8_t* src = img.get_data();
        
        // Convert image to tensor format
        // Assuming image is grayscale and needs to be converted to int16_t
        for (int h = 0; h < PEDESTRIAN_DETECTOR_INPUT_H; h++) {
            for (int w = 0; w < PEDESTRIAN_DETECTOR_INPUT_W; w++) {
                // Convert uint8_t to int16_t (adjust scaling as needed for your model)
                int16_t pixel_value = static_cast<int16_t>(src[h * PEDESTRIAN_DETECTOR_INPUT_W + w]);
                input_tensor->set_element(pixel_value, 0, h, w, 0);
            }
        }
        
        return true;
    }
};