#include <BH1750.h>

void custom_bh1750_helper_begin(BH1750 sensor, int mode_index, int addr = 0x23) {
    BH1750::Mode mode;

    switch (mode_index) {
        case 1: mode = BH1750::CONTINUOUS_HIGH_RES_MODE; break;
        case 2: mode = BH1750::CONTINUOUS_HIGH_RES_MODE_2; break;
        case 3: mode = BH1750::CONTINUOUS_LOW_RES_MODE; break;
        case 4: mode = BH1750::ONE_TIME_HIGH_RES_MODE; break;
        case 5: mode = BH1750::ONE_TIME_HIGH_RES_MODE_2; break;
        case 6: mode = BH1750::ONE_TIME_LOW_RES_MODE; break;
        default: mode = BH1750::CONTINUOUS_HIGH_RES_MODE; break;
    }

    sensor.begin(mode, addr);
}


inline void configureBH1750Mode(BH1750 &sensor, int mode_index) {
    BH1750::Mode mode;

    switch (mode_index) {
        case 1:
            mode = BH1750::CONTINUOUS_HIGH_RES_MODE;
            break;
        case 2:
            mode = BH1750::CONTINUOUS_HIGH_RES_MODE_2;
            break;
        case 3:
            mode = BH1750::CONTINUOUS_LOW_RES_MODE;
            break;
        case 4:
            mode = BH1750::ONE_TIME_HIGH_RES_MODE;
            break;
        case 5:
            mode = BH1750::ONE_TIME_HIGH_RES_MODE_2;
            break;
        case 6:
            mode = BH1750::ONE_TIME_LOW_RES_MODE;
            break;
        default:
            mode = BH1750::CONTINUOUS_HIGH_RES_MODE;
            break;
    }

    sensor.configure(mode);
}