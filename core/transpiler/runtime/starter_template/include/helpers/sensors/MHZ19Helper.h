#ifndef CUSTOM_MHZ19_HELPER_H
#define CUSTOM_MHZ19_HELPER_H

#include <Arduino.h>
#include <MHZ19.h>

/**
 * @brief Create and initialize an MHZ19 CO₂ sensor using specified RX/TX pins.
 *
 * This helper abstracts away UART stream setup and sensor initialization.
 * It automatically creates a hardware serial port, initializes it at the
 * given baud rate, and attaches it to an MHZ19 sensor instance.
 *
 * @param rx_pin GPIO pin connected to the MH-Z19 TX line.
 * @param tx_pin GPIO pin connected to the MH-Z19 RX line.
 * @param baud   Baud rate for UART communication (default = 9600).
 * @return MHZ19* Pointer to a ready-to-use MHZ19 instance.
 */
inline MHZ19* create_mhz19_sensor(int rx_pin, int tx_pin, long baud = 9600) {
    static HardwareSerial mhzSerial(2);   // use UART2 (RX2/TX2) on ESP32

    // Configure UART with provided pins and baud
    mhzSerial.begin(baud, SERIAL_8N1, rx_pin, tx_pin);

    // Create sensor instance
    MHZ19* sensor = new MHZ19();
    sensor->begin(mhzSerial);

    Serial.printf("✅ MHZ19 initialized on RX=%d, TX=%d, baud=%ld\n", rx_pin, tx_pin, baud);
    return sensor;
}

#endif // CUSTOM_MHZ19_HELPER_H
