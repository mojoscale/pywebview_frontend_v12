#include "Arduino.h"

extern "C" void app_main()
{
    initArduino();
    pinMode(4, OUTPUT);
    digitalWrite(4, HIGH);

    delay(2000);

    digitalWrite(4, LOW);
    


}