#include "GP2Y0A21YK.h"

double GP2Y0A21YK::distance(void)
{
    int ad = analogRead(pin);
    double vol = ad * BIT_VOLTAGE;
    double dist = 0.0;
    if(LOW_LIMIT < vol && vol < HIGH_LIMIT)
    {
        // 逆数回帰で解析して近似曲線を求める y = A + (B/x)
        // 理論計算で、 A = -4.82049, B = 34.83012845 
        // 現物合せで、 A = -4.10000, B = 34.4000
        const double A = -4.1000;
        const double B = 34.4000;
        dist = A + B / vol;
    }

    return dist;
}