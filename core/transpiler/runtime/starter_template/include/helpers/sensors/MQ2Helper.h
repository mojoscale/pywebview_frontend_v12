#ifndef MQ2_H
#define MQ2_H

#include <Arduino.h>
#include <math.h>

class MQ2 {
private:
    int _pin;
    float _r0;

public:
    MQ2(int pin) : _pin(pin), _r0(10.0f) {}

    void calibrate_r0(int samples = 50, int delay_ms = 500) {
        float rs_sum = 0.0;
        for (int i = 0; i < samples; i++) {
            float val = analogRead(_pin);
            float vrl = val * (5.0f / 1023.0f);
            float rs = (5.0f - vrl) / vrl * 10.0f;  // RL = 10kΩ
            rs_sum += rs;
            delay(delay_ms);
        }
        _r0 = rs_sum / samples;
    }

    void set_r0(float r0) {
        _r0 = r0;
    }

    float get_r0() const {
        return _r0;
    }

    float read_rs() {
        float val = analogRead(_pin);
        float vrl = val * (5.0f / 1023.0f);
        return (5.0f - vrl) / vrl * 10.0f;
    }

    float read_ratio() {
        return read_rs() / _r0;
    }

    float get_ppm(float a, float b) {
        float ratio = read_ratio();
        return a * pow(ratio, b);
    }
};

#endif
