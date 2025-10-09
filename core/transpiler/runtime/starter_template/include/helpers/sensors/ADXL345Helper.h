#include <Adafruit_ADXL345_U.h>
#include "PyList.h"

PyList<float> custom_adxl345_helper_read_acceleration(Adafruit_ADXL345_Unified* sensor) {
    sensors_event_t event;
    float x = 0.0, y = 0.0, z = 0.0;

    if (sensor->getEvent(&event)) {
        x = event.acceleration.x;
        y = event.acceleration.y;
        z = event.acceleration.z;
    }

    return PyList<float>::from({x, y, z});
}


void setADXLRange(Adafruit_ADXL345_Unified& adxl, int range_val) {
    range_t range_enum;

    switch (range_val) {
        case 0:
            range_enum = ADXL345_RANGE_2_G;
            break;
        case 1:
            range_enum = ADXL345_RANGE_4_G;
            break;
        case 2:
            range_enum = ADXL345_RANGE_8_G;
            break;
        case 3:
            range_enum = ADXL345_RANGE_16_G;
            break;
        default:
            range_enum = ADXL345_RANGE_2_G;
            break;
    }

    adxl.setRange(range_enum);
}




String getADXLRangeText(Adafruit_ADXL345_Unified& adxl) {
    range_t range_enum = adxl.getRange();

    switch (range_enum) {
        case ADXL345_RANGE_2_G:
            return "±2g";
        case ADXL345_RANGE_4_G:
            return "±4g";
        case ADXL345_RANGE_8_G:
            return "±8g";
        case ADXL345_RANGE_16_G:
            return "±16g";
        default:
            return "Unknown range";
    }
}


void setADXLDataRate(Adafruit_ADXL345_Unified& sensor, int rate_val) {
    dataRate_t rate_enum;

    switch (rate_val) {
        case 0:  rate_enum = ADXL345_DATARATE_0_10_HZ; break;
        case 1:  rate_enum = ADXL345_DATARATE_0_20_HZ; break;
        case 2:  rate_enum = ADXL345_DATARATE_0_39_HZ; break;
        case 3:  rate_enum = ADXL345_DATARATE_0_78_HZ; break;
        case 4:  rate_enum = ADXL345_DATARATE_1_56_HZ; break;
        case 5:  rate_enum = ADXL345_DATARATE_3_13_HZ; break;
        case 6:  rate_enum = ADXL345_DATARATE_6_25HZ;  break;
        case 7:  rate_enum = ADXL345_DATARATE_12_5_HZ; break;
        case 8:  rate_enum = ADXL345_DATARATE_25_HZ;   break;
        case 9:  rate_enum = ADXL345_DATARATE_50_HZ;   break;
        case 10: rate_enum = ADXL345_DATARATE_100_HZ;  break;
        case 11: rate_enum = ADXL345_DATARATE_200_HZ;  break;
        case 12: rate_enum = ADXL345_DATARATE_400_HZ;  break;
        case 13: rate_enum = ADXL345_DATARATE_800_HZ;  break;
        case 14: rate_enum = ADXL345_DATARATE_1600_HZ; break;
        case 15: rate_enum = ADXL345_DATARATE_3200_HZ; break;
        default: rate_enum = ADXL345_DATARATE_100_HZ;  // fallback
    }

    sensor.setDataRate(rate_enum);
}



String getADXLDataRateText(Adafruit_ADXL345_Unified& sensor) {
    dataRate_t rate = sensor.getDataRate();

    switch (rate) {
        case ADXL345_DATARATE_0_10_HZ: return "0.10 Hz";
        case ADXL345_DATARATE_0_20_HZ: return "0.20 Hz";
        case ADXL345_DATARATE_0_39_HZ: return "0.39 Hz";
        case ADXL345_DATARATE_0_78_HZ: return "0.78 Hz";
        case ADXL345_DATARATE_1_56_HZ: return "1.56 Hz";
        case ADXL345_DATARATE_3_13_HZ: return "3.13 Hz";
        case ADXL345_DATARATE_6_25HZ:  return "6.25 Hz";
        case ADXL345_DATARATE_12_5_HZ: return "12.5 Hz";
        case ADXL345_DATARATE_25_HZ:   return "25 Hz";
        case ADXL345_DATARATE_50_HZ:   return "50 Hz";
        case ADXL345_DATARATE_100_HZ:  return "100 Hz";
        case ADXL345_DATARATE_200_HZ:  return "200 Hz";
        case ADXL345_DATARATE_400_HZ:  return "400 Hz";
        case ADXL345_DATARATE_800_HZ:  return "800 Hz";
        case ADXL345_DATARATE_1600_HZ: return "1600 Hz";
        case ADXL345_DATARATE_3200_HZ: return "3200 Hz";
        default: return "Unknown rate";
    }
}

