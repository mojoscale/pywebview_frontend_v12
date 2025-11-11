#pragma once
#include <Arduino.h>
#include <NimBLEDevice.h>
#include <functional>

/**
 * @brief A unified, non-static BLE abstraction for ESP32 using NimBLE-Arduino.
 *
 * NimBLESimple wraps NimBLEDevice, NimBLEServer, NimBLEService,
 * NimBLECharacteristic, and NimBLEAdvertising into one easy-to-use class.
 * It behaves as a peripheral by default, exposing a single service and
 * characteristic for bidirectional data.
 */
class NimBLESimple : public NimBLECharacteristicCallbacks, public NimBLEServerCallbacks {
public:
    // Separate callbacks for different events - FIXED: String by value
    using ConnectCallback = void(*)(String clientAddress);
    using DisconnectCallback = void(*)(String clientAddress);
    using WriteCallback = void(*)(String data);
    using ReadCallback = void(*)(void);
    using NotifyCallback = void(*)(void);

    // Constructor that accepts Arduino String
    NimBLESimple(const String& deviceName,
                 const String& serviceUUID,
                 const String& charUUID)
        : _deviceName(deviceName.c_str()),
          _serviceUUID(serviceUUID.c_str()),
          _charUUID(charUUID.c_str()),
          _server(nullptr),
          _service(nullptr),
          _characteristic(nullptr),
          _advertising(nullptr),
          _connected(false),
          _connectCallback(nullptr),
          _disconnectCallback(nullptr),
          _writeCallback(nullptr),
          _readCallback(nullptr),
          _notifyCallback(nullptr) {}

    // Constructor that accepts std::string
    NimBLESimple(const std::string& deviceName,
                 const std::string& serviceUUID,
                 const std::string& charUUID)
        : _deviceName(deviceName),
          _serviceUUID(serviceUUID),
          _charUUID(charUUID),
          _server(nullptr),
          _service(nullptr),
          _characteristic(nullptr),
          _advertising(nullptr),
          _connected(false),
          _connectCallback(nullptr),
          _disconnectCallback(nullptr),
          _writeCallback(nullptr),
          _readCallback(nullptr),
          _notifyCallback(nullptr) {}

    // Constructor that accepts C-style strings
    NimBLESimple(const char* deviceName,
                 const char* serviceUUID,
                 const char* charUUID)
        : _deviceName(deviceName),
          _serviceUUID(serviceUUID),
          _charUUID(charUUID),
          _server(nullptr),
          _service(nullptr),
          _characteristic(nullptr),
          _advertising(nullptr),
          _connected(false),
          _connectCallback(nullptr),
          _disconnectCallback(nullptr),
          _writeCallback(nullptr),
          _readCallback(nullptr),
          _notifyCallback(nullptr) {}

    // ------------------------------------------------------------------------
    // Core lifecycle
    // ------------------------------------------------------------------------

    /**
     * @brief Initialize NimBLE stack and start advertising with configurable properties.
     * @param is_read Enable read property
     * @param is_write Enable write property  
     * @param is_notify Enable notify property
     */
    void begin(bool is_read = true, bool is_write = true, bool is_notify = true) {
        Serial.println("\n=== BLE INITIALIZATION START ===");
        Serial.printf("[NimBLESimple] Instance: %p\n", this);
        Serial.printf("[NimBLESimple] Device Name: %s\n", _deviceName.c_str());
        Serial.printf("[NimBLESimple] Service UUID: %s\n", _serviceUUID.c_str());
        Serial.printf("[NimBLESimple] Characteristic UUID: %s\n", _charUUID.c_str());
        
        // Step 1: Initialize NimBLE
        Serial.println("\n--- Step 1: Initializing NimBLE Device ---");
        Serial.println("Initializing NimBLEDevice...");
        NimBLEDevice::init(_deviceName);
        Serial.printf("NimBLE initialized with device name: %s\n", _deviceName.c_str());
        
        // Step 2: Create Server
        Serial.println("\n--- Step 2: Creating BLE Server ---");
        _server = NimBLEDevice::createServer();
        Serial.printf("Server created: %p\n", _server);
        
        if (!_server) {
            Serial.println("❌ FAILED to create BLE server!");
            return;
        }
        
        // Step 3: Set Server Callbacks
        Serial.println("\n--- Step 3: Setting Server Callbacks ---");
        Serial.printf("Setting server callbacks to: %p (this instance)\n", this);
        _server->setCallbacks(this);
        Serial.println("Server callbacks set");
        
        // Step 4: Create Service
        Serial.println("\n--- Step 4: Creating BLE Service ---");
        Serial.printf("Creating service with UUID: %s\n", _serviceUUID.c_str());
        _service = _server->createService(_serviceUUID);
        Serial.printf("Service created: %p\n", _service);
        
        if (!_service) {
            Serial.println("❌ FAILED to create BLE service!");
            return;
        }
        
        // Step 5: Configure Properties
        Serial.println("\n--- Step 5: Configuring Characteristic Properties ---");
        uint32_t properties = 0;
        if (is_read) {
            properties |= NIMBLE_PROPERTY::READ;
            Serial.println("✓ READ property enabled");
        }
        if (is_write) {
            properties |= NIMBLE_PROPERTY::WRITE | NIMBLE_PROPERTY::WRITE_NR;
            Serial.println("✓ WRITE properties enabled (WRITE + WRITE_NR)");
        }
        if (is_notify) {
            properties |= NIMBLE_PROPERTY::NOTIFY;
            Serial.println("✓ NOTIFY property enabled");
        }
        
        // If no properties are enabled, default to READ and WRITE
        if (properties == 0) {
            properties = NIMBLE_PROPERTY::READ | NIMBLE_PROPERTY::WRITE;
            Serial.println("⚠️  No properties specified, defaulting to READ and WRITE");
        }
        
        Serial.printf("Final properties mask: 0x%08X\n", properties);
        
        // Step 6: Create Characteristic
        Serial.println("\n--- Step 6: Creating Characteristic ---");
        Serial.printf("Creating characteristic with UUID: %s\n", _charUUID.c_str());
        _characteristic = _service->createCharacteristic(_charUUID, properties);
        Serial.printf("Characteristic created: %p\n", _characteristic);
        
        if (!_characteristic) {
            Serial.println("❌ FAILED to create BLE characteristic!");
            return;
        }
        
        // Step 7: Set Characteristic Callbacks
        Serial.println("\n--- Step 7: Setting Characteristic Callbacks ---");
        Serial.printf("Setting characteristic callbacks to: %p (this instance)\n", this);
        _characteristic->setCallbacks(this);
        Serial.println("Characteristic callbacks set");
        
        // Step 8: Start Service
        Serial.println("\n--- Step 8: Starting BLE Service ---");
        bool serviceStarted = _service->start();
        Serial.printf("Service start result: %s\n", serviceStarted ? "SUCCESS" : "FAILED");
        
        if (!serviceStarted) {
            Serial.println("❌ FAILED to start BLE service!");
            return;
        }
        
        // Step 9: Setup Advertising
        Serial.println("\n--- Step 9: Setting up Advertising ---");
        _advertising = NimBLEDevice::getAdvertising();
        

        
        if (!_advertising) {
            Serial.println("❌ FAILED to get advertising object!");
            return;
        }

        _advertising->setName(_deviceName.c_str());
        
        Serial.printf("Adding service UUID to advertising: %s\n", _serviceUUID.c_str());
        _advertising->addServiceUUID(_serviceUUID);
        
        // Step 10: Start Advertising
        Serial.println("\n--- Step 10: Starting Advertising ---");
        bool advertisingStarted = _advertising->start();
        Serial.printf("Advertising start result: %s\n", advertisingStarted ? "SUCCESS" : "FAILED");
        
        // Final Status
        Serial.println("\n=== BLE INITIALIZATION COMPLETE ===");
        Serial.printf("Device Address: %s\n", NimBLEDevice::getAddress().toString().c_str());
        
        if (_server) {
            Serial.printf("Server Connected Count: %d\n", _server->getConnectedCount());
        }
        
        Serial.printf("Instance State - Connected: %s\n", _connected ? "YES" : "NO");
        Serial.printf("Callback Status - Connect: %s, Write: %s, Read: %s, Notify: %s\n",
                      _connectCallback ? "SET" : "NULL",
                      _writeCallback ? "SET" : "NULL", 
                      _readCallback ? "SET" : "NULL",
                      _notifyCallback ? "SET" : "NULL");
        
        // Test characteristic access
        if (_characteristic) {
            Serial.printf("Characteristic UUID: %s\n", _characteristic->getUUID().toString().c_str());
            Serial.printf("Characteristic Properties: 0x%08X\n", _characteristic->getProperties());
        }
        
        Serial.println("=== READY FOR CONNECTIONS ===\n");
        
        // Small delay to ensure serial output is flushed
        delay(100);
    }


    /**
     * @brief Stop advertising and deinitialize BLE.
     */
    void stop() {
        if (_advertising) _advertising->stop();

        if (_server) {
            auto connectedCount = NimBLEDevice::getServer()->getConnectedCount();
            if (connectedCount > 0) {
                for (uint16_t i = 0; i < connectedCount; i++) {
                    NimBLEDevice::getServer()->disconnect(i);
                }
            }
        }

        NimBLEDevice::deinit(true);
        Serial.println("[NimBLESimple] BLE stopped");
    }

    // ------------------------------------------------------------------------
    // Data send / receive
    // ------------------------------------------------------------------------

    /**
     * @brief Send data to the connected central via notification.
     * @param data String or binary payload to send.
     */
    void send(const std::string& data) {
        if (!_characteristic) return;
        _characteristic->setValue(data);
        _characteristic->notify();
        Serial.printf("[NimBLESimple] Sent: %s\n", data.c_str());
    }

    // Overload for Arduino String
    void send(const String& data) {
        send(std::string(data.c_str()));
    }

    // Overload for C-style string
    void send(const char* data) {
        send(std::string(data));
    }

    // ------------------------------------------------------------------------
    // Callback registration methods
    // ------------------------------------------------------------------------

    /**
     * @brief Set callback for when a client connects
     * @param callback Function that receives client address
     */
    void setConnectCallback(ConnectCallback callback) {
        _connectCallback = callback;
    }

    /**
     * @brief Set callback for when a client disconnects
     * @param callback Function that receives client address
     */
    void setDisconnectCallback(DisconnectCallback callback) {
        _disconnectCallback = callback;
    }

    /**
     * @brief Set callback for when data is written to characteristic
     * @param callback Function that receives the written data
     */
    void setWriteCallback(WriteCallback callback) {
        _writeCallback = callback;
    }

    /**
     * @brief Set callback for when characteristic is read
     * @param callback Function with no parameters
     */
    void setReadCallback(ReadCallback callback) {
        _readCallback = callback;
    }

    /**
     * @brief Set callback for when notification is sent
     * @param callback Function with no parameters
     */
    void setNotifyCallback(NotifyCallback callback) {
        _notifyCallback = callback;
    }

    // ------------------------------------------------------------------------
    // Status and configuration
    // ------------------------------------------------------------------------

    /**
     * @return True if a central is connected.
     */
    bool isConnected() const { return _connected; }

    /**
     * @brief Adjust transmit power.
     * @param dbm Power level in dBm.
     */
    void setPower(int8_t dbm) {
        NimBLEDevice::setPower(dbm);
        Serial.printf("[NimBLESimple] TX power set to %d dBm\n", dbm);
    }

    /**
     * @brief Configure pairing and bonding security.
     */
    void setSecurity(bool bonding = true, bool mitm = false, bool sc = false) {
        NimBLEDevice::setSecurityAuth(bonding, mitm, sc);
        Serial.println("[NimBLESimple] Security parameters applied");
    }

    /**
     * @return BLE MAC address of the ESP32 as Arduino String.
     */
    String getAddress() const {
        return String(NimBLEDevice::getAddress().toString().c_str());
    }

    // Overload for std::string if needed
    std::string getAddressStd() const {
        return NimBLEDevice::getAddress().toString();
    }

    /**
     * @brief Check if BLE is currently advertising
     * @return True if advertising is active
     */
    bool isAdvertising() const {
        return _advertising != nullptr;
    }

    /**
     * @brief Restart advertising if it stopped
     */
    void restartAdvertising() {
        if (_advertising && !_connected) {
            _advertising->start();
            Serial.println("[NimBLESimple] Advertising restarted");
        }
    }


    /**
     * @brief Print comprehensive debug information about the BLE state
     */
    void debugState() {
        Serial.println("\n=== NIMBLESIMPLE DEBUG STATE ===");
        Serial.printf("Instance: %p\n", this);
        Serial.printf("Server: %p\n", _server);
        Serial.printf("Service: %p\n", _service);
        Serial.printf("Characteristic: %p\n", _characteristic);
        Serial.printf("Advertising: %p\n", _advertising);
        Serial.printf("Connected: %s\n", _connected ? "YES" : "NO");
        
        if (_server) {
            Serial.printf("Server Connected Count: %d\n", _server->getConnectedCount());
        }
        
        if (_characteristic) {
            Serial.printf("Characteristic UUID: %s\n", _characteristic->getUUID().toString().c_str());
            Serial.printf("Characteristic Properties: 0x%08X\n", _characteristic->getProperties());
        }
        
        Serial.printf("User Callbacks - Connect: %p, Disconnect: %p, Write: %p, Read: %p, Notify: %p\n",
                      _connectCallback, _disconnectCallback, _writeCallback, 
                      _readCallback, _notifyCallback);
        
        Serial.printf("Device Address: %s\n", NimBLEDevice::getAddress().toString().c_str());
        Serial.println("=== DEBUG STATE END ===\n");
    }

    // ------------------------------------------------------------------------
    // BLE Server Callbacks (connection management)
    // ------------------------------------------------------------------------

    void onConnect(NimBLEServer* pServer, NimBLEConnInfo& connInfo) override {
        _connected = true;
        
        String clientAddress = connInfo.getAddress().toString().c_str();
        
        Serial.println("🎯 onConnect CALLBACK TRIGGERED!");
        Serial.printf("Client connected: %s\n", clientAddress.c_str());
        Serial.printf("Connected clients: %d\n", pServer->getConnectedCount());
        
        if (_connectCallback) {
            Serial.println("Calling connect callback...");
            _connectCallback(clientAddress);
        }
        
        Serial.println("[NimBLESimple] Central connected");
    }

    void onDisconnect(NimBLEServer* pServer, NimBLEConnInfo& connInfo, int reason) override {
        _connected = false;
        
        String clientAddress = connInfo.getAddress().toString().c_str();
        
        Serial.println("🎯 onDisconnect CALLBACK TRIGGERED!");
        Serial.printf("Client disconnected: %s, reason: %d\n", clientAddress.c_str(), reason);
        Serial.printf("Remaining connected clients: %d\n", pServer->getConnectedCount());
        
        if (_disconnectCallback) {
            Serial.println("Calling disconnect callback...");
            _disconnectCallback(clientAddress);
        }
        
        Serial.println("[NimBLESimple] Central disconnected, restarting advertising...");
        
        // Small delay before restarting advertising
        delay(100);
        
        if (_advertising) {
            bool started = _advertising->start();
            Serial.printf("Advertising restarted: %s\n", started ? "SUCCESS" : "FAILED");
        }
    }
            
    // ------------------------------------------------------------------------
    // BLE Characteristic Callbacks (data events)
    // ------------------------------------------------------------------------

    // ------------------------------------------------------------------------
    // BLE Characteristic Callbacks (data events)
    // ------------------------------------------------------------------------

    void onWrite(NimBLECharacteristic* pCharacteristic, NimBLEConnInfo& connInfo) override {
        Serial.println("🎯 onWrite CALLBACK TRIGGERED!");
        
        // Check if this is the right characteristic
        Serial.printf("Characteristic UUID: %s\n", pCharacteristic->getUUID().toString().c_str());
        Serial.printf("Expected UUID: %s\n", _charUUID.c_str());
        Serial.printf("Client Address: %s\n", connInfo.getAddress().toString().c_str());
        
        std::string value = pCharacteristic->getValue();
        String data = String(value.c_str());
        
        Serial.printf("Received data length: %d bytes\n", value.length());
        Serial.printf("Received data: %s\n", data.c_str());
        Serial.printf("Data as hex: ");
        for (char c : value) {
            Serial.printf("%02X ", (unsigned char)c);
        }
        Serial.println();
        
        if (_writeCallback) {
            Serial.println("Calling write callback...");
            _writeCallback(data);
        } else {
            Serial.println("❌ No write callback registered!");
        }
        
        Serial.println("✅ onWrite COMPLETED");
    }

    void onRead(NimBLECharacteristic* pCharacteristic, NimBLEConnInfo& connInfo) override {
        Serial.println("🎯 onRead CALLBACK TRIGGERED!");
        Serial.printf("Client Address: %s\n", connInfo.getAddress().toString().c_str());
        
        if (_readCallback) {
            Serial.println("Calling read callback...");
            _readCallback();
        }
        
        Serial.println("[NimBLESimple] Characteristic read");
    }

    void onNotify(NimBLECharacteristic* pCharacteristic) {
        Serial.println("🎯 onNotify CALLBACK TRIGGERED!");
        
        if (_notifyCallback) {
            Serial.println("Calling notify callback...");
            _notifyCallback();
        }
        
        Serial.println("[NimBLESimple] Notification sent");
    }

    void onStatus(NimBLECharacteristic* pCharacteristic, int code) {
        // Optional: Handle status events if needed
        Serial.printf("[NimBLESimple] Characteristic status: %d\n", code);
    }

    /*void onRead(NimBLECharacteristic* pCharacteristic) {
        Serial.println("🎯 onRead CALLBACK TRIGGERED!");
        
        if (_readCallback) {
            Serial.println("Calling read callback...");
            _readCallback();
        }
        
        Serial.println("[NimBLESimple] Characteristic read");
    }

    void onNotify(NimBLECharacteristic* pCharacteristic) {
        Serial.println("🎯 onNotify CALLBACK TRIGGERED!");
        
        if (_notifyCallback) {
            Serial.println("Calling notify callback...");
            _notifyCallback();
        }
        
        Serial.println("[NimBLESimple] Notification sent");
    }

    void onStatus(NimBLECharacteristic* pCharacteristic, int code) {
        // Optional: Handle status events if needed
        Serial.printf("[NimBLESimple] Characteristic status: %d\n", code);
    }*/

private:
    std::string _deviceName;
    std::string _serviceUUID;
    std::string _charUUID;

    NimBLEServer* _server;
    NimBLEService* _service;
    NimBLECharacteristic* _characteristic;
    NimBLEAdvertising* _advertising;

    bool _connected;
    
    // Separate callbacks for different events
    ConnectCallback _connectCallback;
    DisconnectCallback _disconnectCallback;
    WriteCallback _writeCallback;
    ReadCallback _readCallback;
    NotifyCallback _notifyCallback;
};