#pragma once
#include <VisionCore/VisionModel.h>
extern const uint8_t _binary_face_espdl_start[] asm("_binary_face_espdl_start");

class FaceDetector : public VisionModel {
public:
    FaceDetector() : VisionModel(_binary_face_espdl_start) {
        Serial.println("[FaceDetector] Ready.");
    }

    bool detect(const uint8_t* frame, int width, int height) {
        return infer(frame, width, height);
    }

protected:
    bool postprocess() override {
        float* out = (float*)output_tensor->get_data();
        float conf = out[0];
        Serial.printf("[FaceDetector] Confidence: %.3f\n", conf);
        return conf > 0.5f;
    }
};
