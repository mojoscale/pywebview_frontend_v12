#ifdef ESP32
  #include <HardwareSerial.h>
#elif defined(ESP8266)
  #include <HardwareSerial.h>
#endif

/**
 * Custom begin() helper for HardwareSerial that handles platform differences.
 * 
 * Converts generic config format (0x06 for 8N1, etc.) to platform-specific
 * SerialConfig on ESP8266, while passing through directly on ESP32.
 * 
 * @param serial Reference to HardwareSerial instance
 * @param baud Baud rate (9600, 115200, etc.)
 * @param config Configuration byte (0x06 = SERIAL_8N1, etc.)
 * 
 * Platform Notes:
 * - ESP32: config passed as-is to begin(baud, config)
 * - ESP8266: config converted to SerialConfig enum before begin(baud, config)
 */
void custom_hardware_serial_begin(HardwareSerial serial, unsigned long baud, int config) {
    
#ifdef ESP32
    // ESP32: Pass config directly
    serial.begin(baud, config);
    
#elif defined(ESP8266)
    // ESP8266: Convert config byte to SerialConfig enum
    SerialConfig esp8266_config;
    
    // Map generic config format to ESP8266 SerialConfig
    // Format: config byte encodes [data bits][parity][stop bits]
    // Common values:
    // 0x06 -> SERIAL_8N1 (8 data, no parity, 1 stop)
    // 0x0C -> SERIAL_8N2 (8 data, no parity, 2 stop)
    // 0x16 -> SERIAL_8E1 (8 data, even parity, 1 stop)
    // 0x26 -> SERIAL_8O1 (8 data, odd parity, 1 stop)
    
    switch (config) {
        case 0x06:  // 8N1
            esp8266_config = SERIAL_8N1;
            break;
        case 0x0C:  // 8N2
            esp8266_config = SERIAL_8N2;
            break;
        case 0x16:  // 8E1
            esp8266_config = SERIAL_8E1;
            break;
        case 0x26:  // 8O1
            esp8266_config = SERIAL_8O1;
            break;
        case 0x1E:  // 8E2
            esp8266_config = SERIAL_8E2;
            break;
        case 0x2E:  // 8O2
            esp8266_config = SERIAL_8O2;
            break;
        default:
            // Fallback to SERIAL_8N1 for unknown config
            esp8266_config = SERIAL_8N1;
            Serial.print("⚠️  Unknown serial config: 0x");
            Serial.print(config, HEX);
            Serial.println(" - using SERIAL_8N1");
            break;
    }
    
    serial.begin(baud, esp8266_config);
    
#else
    // Fallback for other platforms
    serial.begin(baud, config);
#endif
}