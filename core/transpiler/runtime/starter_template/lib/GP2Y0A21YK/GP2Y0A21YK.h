#ifndef __GP2Y0A21YK_H__
#define __GP2Y0A21YK_H__
#include <Arduino.h>
#include <Wire.h>

//-----------------------------------------
// Platform-specific default pin
#ifdef ESP32
  #define DEF_PIN (36)
#elif defined(ESP8266)
  #define DEF_PIN (A0)
#else
  #define DEF_PIN (A3)  // fallback
#endif

#define OPERATING_VOLTAGE (5.0)

// Resolution differs by platform
#ifdef ESP32
  #define RESOLUTION (4096.0)  // ESP32 has 12-bit ADC
#elif defined(ESP8266)
  #define RESOLUTION (1024.0)  // ESP8266 has 10-bit ADC
#else
  #define RESOLUTION (1024.0)  // fallback
#endif

#define BIT_VOLTAGE (OPERATING_VOLTAGE / RESOLUTION)
#define LOW_LIMIT  (0.0)
#define HIGH_LIMIT (2.6)
//-----------------------------------------

class GP2Y0A21YK
{
public:
    GP2Y0A21YK(uint8_t analog_pin = DEF_PIN)
    {
        pin = analog_pin;
        pinMode(pin, INPUT);
    };
    ~GP2Y0A21YK()
    {
        
    };
    
    double distance(void);
private:
    uint8_t pin;
};

#endif