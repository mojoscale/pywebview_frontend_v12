#pragma once
#include <Arduino.h>
#include <SPIFFS.h>

//
// ESP-DL — correct includes
//
#include "dl/model/model.hpp"
#include "dl/tensor/tensor.hpp"
#include "dl/tool/dl_tool.hpp"
#include "dl/dl_define.hpp"
#include "dl/vision/image.hpp"
#include "dl/vision/preprocess.hpp"

#include <esp_heap_caps.h>

#define PEDESTRIAN_MODEL_PATH "/pedestrian_detector.espdl"
#define INPUT_W 96
#define INPUT_H 96
#define INPUT_C 1
#define NUM_CLASSES 2

class PedestrianDetector {
public:
    PedestrianDetector(float threshold = 0.6f)
        : threshold_(threshold), ready_(false) {}

    bool begin() {
        Serial.println("[PedestrianDetector] Initializing…");

        if (!SPIFFS.begin(true)) {
            Serial.println("❌ SPIFFS mount failed");
            return false;
        }

        if (!load_model()) {
            Serial.println("❌ Model load failed");
            return false;
        }

        ready_ = true;
        Serial.println("✅ PedestrianDetector ready");
        return true;
    }

    bool isReady() const { return ready_; }

    void setThreshold(float t) { threshold_ = t; }

    //
    // MAIN API — pass an ESP-DL Image
    //
    bool detect(const dl::image::Image &img)
    {
        if (!ready_) {
            Serial.println("❌ Detector not initialized");
            return false;
        }

        if (!img.is_valid()) {
            Serial.println("❌ Invalid image input");
            return false;
        }

        // 1. Preprocess -> resized grayscale tensor (1,96,96,1)
        dl::TensorBase input_tensor;
        if (!make_input(img, input_tensor)) {
            Serial.println("❌ Failed to create input tensor");
            return false;
        }

        // 2. Forward pass
        dl::TensorBase output;
        auto status = model_.forward(input_tensor, output);

        if (status != dl::Status::OK) {
            Serial.printf("❌ Inference failed: %d\n", (int)status);
            return false;
        }

        if (output.size() != NUM_CLASSES) {
            Serial.println("❌ Output tensor shape mismatch");
            return false;
        }

        // 3. Convert output (int8 or int16) → float
        float logits[NUM_CLASSES];

        for (int i = 0; i < NUM_CLASSES; i++) {
            logits[i] = dl::tool::dequantize(output.get_element<int8_t>(i),
                                             output.get_scale(),
                                             output.get_zero_point());
        }

        // 4. Softmax
        float exps[NUM_CLASSES];
        float sum = 0.0f;
        for (int i = 0; i < NUM_CLASSES; i++) {
            exps[i] = expf(logits[i]);
            sum += exps[i];
        }
        float no_person = exps[0] / sum;
        float yes_person = exps[1] / sum;

        Serial.printf("[PedestrianDetector] Scores: no=%.3f yes=%.3f\n",
                      no_person, yes_person);

        return yes_person >= threshold_;
    }

private:
    float threshold_;
    bool ready_;
    dl::Model model_;

    //
    // ---------------- LOAD .ESP-DL MODEL ----------------
    //
    bool load_model()
    {
        if (!SPIFFS.exists(PEDESTRIAN_MODEL_PATH)) {
            Serial.printf("❌ Model file missing: %s\n", PEDESTRIAN_MODEL_PATH);
            return false;
        }

        File f = SPIFFS.open(PEDESTRIAN_MODEL_PATH, "r");
        if (!f) {
            Serial.println("❌ Failed to open model");
            return false;
        }

        size_t size = f.size();
        uint8_t *buffer = (uint8_t *)heap_caps_malloc(size, MALLOC_CAP_SPIRAM | MALLOC_CAP_DEFAULT);

        if (!buffer) {
            Serial.println("❌ Memory alloc failed for model");
            f.close();
            return false;
        }

        f.read(buffer, size);
        f.close();

        auto status = model_.load(buffer, size);

        // You can free buffer now — ESP-DL copies as needed
        heap_caps_free(buffer);

        if (status != dl::Status::OK) {
            Serial.printf("❌ Model load error: %d\n", (int)status);
            return false;
        }

        Serial.printf("📦 Model loaded (%d bytes)\n", size);
        return true;
    }

    //
    // ---------- Convert ESP-DL Image → Input Tensor (NHWC) ----------
    //
    bool make_input(const dl::image::Image &img, dl::TensorBase &tensor_out)
    {
        // Resize the input
        auto resized = dl::image::resize(img, INPUT_W, INPUT_H);
        if (!resized.is_valid()) {
            Serial.println("❌ Resize failed");
            return false;
        }

        // Convert to grayscale if needed
        dl::image::Image gray;
        if (resized.channel() == 3) {
            gray = dl::image::rgb2gray(resized);
        } else {
            gray = resized;
        }

        if (!gray.is_valid()) {
            Serial.println("❌ Grayscale conversion failed");
            return false;
        }

        // Create NHWC tensor
        tensor_out = dl::TensorBase({1, INPUT_H, INPUT_W, INPUT_C},
                                    dl::DataType::INT8);

        int8_t *dst = tensor_out.data<int8_t>();

        // Normalize manually: uint8 → int8
        for (int i = 0; i < INPUT_H * INPUT_W; i++) {
            int v = gray.data()[i];
            dst[i] = (int8_t)(v - 128);  // simple normalization
        }

        return true;
    }
};
