#pragma once
#include <Arduino.h>
#include <esp_dl.h>
#include <map>
#include <string>

class VisionModel {
protected:
    dl::Model* model = nullptr;
    dl::TensorBase* input_tensor = nullptr;
    dl::TensorBase* output_tensor = nullptr;
    int input_width = 0, input_height = 0, input_channels = 0;

public:
    VisionModel(const uint8_t* model_data) {
        model = new dl::Model((const char*)model_data, fbs::MODEL_LOCATION_IN_FLASH_RODATA);
        auto inputs = model->get_inputs();
        auto outputs = model->get_outputs();
        input_tensor = inputs.begin()->second;
        output_tensor = outputs.begin()->second;
        auto shape = input_tensor->get_shape();
        input_height = shape[1];
        input_width = shape[2];
        input_channels = shape[3];
        Serial.printf("[VisionModel] Model loaded (%dx%dx%d)\n", input_width, input_height, input_channels);
    }

    virtual ~VisionModel() { delete model; }

    bool infer(const uint8_t* frame, int width, int height) {
        preprocess(frame, width, height);
        model->run({input_tensor});
        return postprocess();
    }

protected:
    virtual void preprocess(const uint8_t* frame, int width, int height) {
        size_t sz = input_tensor->get_size();
        memcpy(input_tensor->get_data(), frame, min((size_t)width * height * input_channels, sz));
    }

    virtual bool postprocess() = 0;
};
