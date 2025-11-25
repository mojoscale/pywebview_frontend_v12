#include <Arduino.h>
#include "esp32-hal-ledc.h"
#include "ArduinoHelper.h"

#ifdef ESP32

void analogWrite(int pin, int value) {
    Serial.printf("[DEBUG] overriding Arduino analogWrite for pin %d, value %d\n", pin, value);

    static bool initialized[16] = {false};
    static int attachedPin[16] = {-1};
    int channel = pin % 16;

    if (!initialized[channel] || attachedPin[channel] != pin) {
        ledcSetup(channel, 5000, 8);
        ledcAttachPin(pin, channel);
        ledcWrite(channel, 0);
        initialized[channel] = true;
        attachedPin[channel] = pin;
        delay(2);
    }

    ledcWrite(channel, value);
}

#endif  // ESP32

#ifdef ESP8266
void analogWrite(int pin, int value) {
    ::analogWrite(pin, value);
}
#endif
