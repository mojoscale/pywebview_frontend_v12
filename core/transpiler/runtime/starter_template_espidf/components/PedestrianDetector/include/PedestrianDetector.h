#pragma once
#include <Arduino.h>
#include <SPIFFS.h>
#include <vector>

// Correct ESP-DL includes
#include "dl_image.hpp"
#include "pedestrian_detect_model.hpp"  // Your generated model header

#define PEDESTRIAN_MODEL_PATH "/spiffs/pedestrian_detector.bin"

// Simple image structure to hold data + auto-detected dimensions
struct SimpleImage {
    const uint8_t* data;
    int width;
    int height;
    int channels;
    
    SimpleImage(const uint8_t* d, int w, int h, int c = 1) : data(d), width(w), height(h), channels(c) {}
    SimpleImage(const uint8_t* d) : data(d), width(0), height(0), channels(1) {} // Auto-detect
};

class PedestrianDetector {
private:
    bool model_loaded;
    float threshold;
    pedestrian_detect_model model; // Your actual generated model
    
public:
    PedestrianDetector(float conf_threshold = 0.6) : 
        model_loaded(false), threshold(conf_threshold) {}

    ~PedestrianDetector() {
        // ESP-DL models usually handle their own cleanup
    }

    bool begin() {
        Serial.println("[PedestrianDetector] Initializing...");
        
        if (!SPIFFS.begin(true)) {
            Serial.println("❌ SPIFFS mount failed");
            return false;
        }

        // Check if model file exists (if using external model)
        if (!SPIFFS.exists(PEDESTRIAN_MODEL_PATH)) {
            Serial.printf("⚠️ Model file not found: %s (using compiled model)\n", PEDESTRIAN_MODEL_PATH);
        }

        model_loaded = true;
        Serial.println("✅ PedestrianDetector ready");
        return true;
    }

    // MAIN DETECTION METHOD - auto-detects dimensions
    bool detect(const uint8_t* image_data) {
        if (!model_loaded) {
            Serial.println("❌ Model not loaded");
            return false;
        }

        if (!image_data) {
            Serial.println("❌ No image data provided");
            return false;
        }

        // Auto-detect image dimensions
        SimpleImage img(image_data);
        if (!detect_image_dimensions(img)) {
            Serial.println("❌ Failed to auto-detect image dimensions");
            return false;
        }

        Serial.printf("🖼️ Auto-detected image: %dx%d, %d channel(s)\n", 
                     img.width, img.height, img.channels);

        // Preprocess image to model's expected tensor format
        auto input_tensor = preprocess_image(img);
        
        if (input_tensor.size == 0) {
            Serial.println("❌ Failed to preprocess image");
            return false;
        }

        // Run inference
        auto model_output = model.forward(input_tensor);
        
        // Process output and return true if detection meets threshold
        return process_output_simple(model_output);
    }

    // Overload for manual dimension specification (backward compatible)
    bool detect(const uint8_t* image_data, int width, int height, int channels = 1) {
        SimpleImage img(image_data, width, height, channels);
        return detect(img);
    }

    bool isReady() const { 
        return model_loaded; 
    }

    void setThreshold(float t) { 
        threshold = t; 
    }

private:
    bool detect_image_dimensions(SimpleImage& img) {
        // Try common ESP32-CAM formats first
        
        // Method 1: Check for common resolutions
        const int common_widths[] = {160, 320, 640, 800};
        const int common_heights[] = {120, 240, 480, 600};
        
        // For ESP32-CAM, typical configurations:
        // - QQVGA: 160x120
        // - QVGA: 320x240  
        // - VGA: 640x480
        // - SVGA: 800x600
        
        // Try to detect based on common aspect ratios and sizes
        // This is a heuristic approach - you might need to adjust for your camera
        
        // For now, default to a common ESP32-CAM resolution
        // You can enhance this with more sophisticated detection
        img.width = 320;
        img.height = 240;
        img.channels = 1; // Assume grayscale for ESP32-CAM
        
        Serial.printf("🔍 Assuming common ESP32-CAM resolution: %dx%d\n", img.width, img.height);
        return true;
        
        // Alternative: If you have image format information, use it
        // For JPEG images, you could parse the header to get exact dimensions
        // For raw formats, you need to know the format from camera configuration
    }

    dl::Tensor<int8_t> preprocess_image(const SimpleImage& img) {
        // Model expected dimensions - adjust based on your actual model
        const int MODEL_HEIGHT = 96;
        const int MODEL_WIDTH = 96;
        const int MODEL_CHANNELS = 1;

        // Create input tensor with correct shape [1, height, width, channels]
        dl::Tensor<int8_t> input_tensor({1, MODEL_HEIGHT, MODEL_WIDTH, MODEL_CHANNELS});

        // Simple resize and normalization
        for (int y = 0; y < MODEL_HEIGHT; y++) {
            for (int x = 0; x < MODEL_WIDTH; x++) {
                // Map coordinates from input image to model input size
                int src_x = (x * img.width) / MODEL_WIDTH;
                int src_y = (y * img.height) / MODEL_HEIGHT;
                
                int src_idx = src_y * img.width + src_x;
                int dst_idx = y * MODEL_WIDTH + x;
                
                if (img.channels == 1) {
                    // Grayscale - simple copy with normalization
                    input_tensor[dst_idx] = img.data[src_idx] - 128;
                } else {
                    // RGB to grayscale conversion
                    int rgb_idx = src_idx * img.channels;
                    uint8_t gray_val = (uint8_t)(
                        0.299f * img.data[rgb_idx] + 
                        0.587f * img.data[rgb_idx + 1] + 
                        0.114f * img.data[rgb_idx + 2]
                    );
                    input_tensor[dst_idx] = gray_val - 128;
                }
            }
        }
        
        return input_tensor;
    }

    bool process_output_simple(dl::Tensor<float>& output) {
        // Simplified output processing - returns true if pedestrian detected
        
        if (output.shape[1] >= 2) {
            float no_pedestrian_score = output[0];
            float pedestrian_score = output[1];
            
            float pedestrian_prob = pedestrian_score; // Simplified
            // For proper softmax: exp(pedestrian_score) / (exp(no_pedestrian_score) + exp(pedestrian_score))
            
            Serial.printf("[PedestrianDetector] Score: %.3f, Threshold: %.3f\n", 
                         pedestrian_prob, threshold);
            
            return pedestrian_prob >= threshold;
        }
        else if (output.shape[1] == 1) {
            float detection_score = output[0];
            Serial.printf("[PedestrianDetector] Score: %.3f, Threshold: %.3f\n", 
                         detection_score, threshold);
            return detection_score >= threshold;
        }
        
        Serial.println("❌ Unexpected output format");
        return false;
    }
};