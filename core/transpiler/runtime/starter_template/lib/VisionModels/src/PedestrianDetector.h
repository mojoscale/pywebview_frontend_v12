#pragma once
#include <Arduino.h>
#include <EloquentTinyML.h>
#include "helpers/peripherals/ESPCameraHelper.h"

// Include your EloquentTinyML model header here.
// It should define something like:
//   extern const unsigned char pedestrian_model[];
//   extern const int pedestrian_model_len;
#include "pedestrian_detector.h"

#define PEDESTRIAN_DETECTOR_TENSOR_ARENA_SIZE (90 * 1024)
#define PEDESTRIAN_DETECTOR_INPUTS  (96 * 96)
#define PEDESTRIAN_DETECTOR_OUTPUTS 2

class PedestrianDetector {
public:
    PedestrianDetector() :
        model_loaded(false),
        threshold(0.6f) {}

    bool begin() {
        Serial.println("🔄 Initializing PedestrianDetector...");

        // Initialize TinyML model directly from the header array
        if (!ml.begin(pedestrian_model)) {
            Serial.println("❌ Failed to initialize TinyML model (invalid header or insufficient memory)");
            return false;
        }

        model_loaded = true;
        Serial.println("✅ PedestrianDetector ready (EloquentTinyML static model)");
        return true;
    }

    bool detect(const Image& img) {
        if (!model_loaded) {
            Serial.println("❌ Model not loaded — call begin() first");
            return false;
        }
        if (!img.is_valid()) {
            Serial.println("❌ Invalid image");
            return false;
        }

        prepare_input(img);

        float output_buffer[PEDESTRIAN_DETECTOR_OUTPUTS] = {0};
        ml.predict(input_buffer.data(), output_buffer);

        Serial.printf("[PedestrianDetector] Scores: [no_person=%.3f, person=%.3f]\n",
                      output_buffer[0], output_buffer[1]);

        return postprocess(output_buffer);
    }

protected:
    bool postprocess(const float* output) {
        float person_conf = output[1];
        return person_conf >= threshold;
    }

    void prepare_input(const Image& img) {
        const uint8_t* pixels = img.get_data();
        input_buffer.resize(PEDESTRIAN_DETECTOR_INPUTS);

        for (int i = 0; i < PEDESTRIAN_DETECTOR_INPUTS && i < img.size(); i++) {
            input_buffer[i] = ((float)pixels[i] - 128.0f) / 128.0f;
        }
    }

private:
    bool model_loaded;
    float threshold;
    std::vector<float> input_buffer;

    Eloquent::TinyML::TfLite<
        PEDESTRIAN_DETECTOR_INPUTS,
        PEDESTRIAN_DETECTOR_OUTPUTS,
        PEDESTRIAN_DETECTOR_TENSOR_ARENA_SIZE
    > ml;
};
