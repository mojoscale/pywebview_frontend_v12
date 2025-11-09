#ifndef BLESIMPLE_H
#define BLESIMPLE_H

#include <Arduino.h>
#include <BLEDevice.h>
#include <BLEUtils.h>
#include <BLEServer.h>
#include <BLEClient.h>
#include <BLEScan.h>
#include <BLEAdvertisedDevice.h>
#include <BLERemoteService.h>
#include <BLERemoteCharacteristic.h>
#include "PyList.h"
#include "PyDict.h"
#include <map>

class BLESimple {
private:
    String deviceName;
    String mode;
    bool connected;
    String userServiceUUID;

    BLEServer* pServer = nullptr;
    BLEClient* pClient = nullptr;
    BLEScan* pScan = nullptr;

    std::map<std::string, BLEService*> services;
    PyDict<String> serviceCharMap;
    PyList<BLECharacteristic*> createdCharacteristics;

    static void (*onConnectCallback)();
    static void (*onDisconnectCallback)();

    std::map<std::string, void (*)(String)> writeCallbacks;
    std::map<std::string, void (*)(String)> notifyCallbacks;

    class ServerCallbacks : public BLEServerCallbacks {
    private:
        BLESimple* parent;
    public:
        ServerCallbacks(BLESimple* p) : parent(p) {}
        void onConnect(BLEServer* pServer) override {
            Serial.println("[BLESimple] Peripheral connected");
            parent->connected = true;
            if (onConnectCallback) onConnectCallback();
        }
        void onDisconnect(BLEServer* pServer) override {
            Serial.println("[BLESimple] Peripheral disconnected");
            parent->connected = false;
            if (onDisconnectCallback) onDisconnectCallback();
        }
    };

    class CharacteristicCallbacks : public BLECharacteristicCallbacks {
    private:
        BLESimple* parent;
        std::string uuid;
    public:
        CharacteristicCallbacks(BLESimple* p, const std::string& u) : parent(p), uuid(u) {}

        void onWrite(BLECharacteristic* pCharacteristic) override {
            std::string val = pCharacteristic->getValue();
            Serial.printf("[BLESimple] onWrite triggered for UUID: %s with value: %s\n", uuid.c_str(), val.c_str());
            if (parent->writeCallbacks.count(uuid)) {
                parent->writeCallbacks[uuid](String(val.c_str()));
            }
        }

        void onNotify(BLECharacteristic* pCharacteristic) override {
            std::string val = pCharacteristic->getValue();
            Serial.printf("[BLESimple] onNotify triggered for UUID: %s with value: %s\n", uuid.c_str(), val.c_str());
            if (parent->notifyCallbacks.count(uuid)) {
                parent->notifyCallbacks[uuid](String(val.c_str()));
            }
        }
    };

public:
    BLESimple(const String& name, const String& mode = "peripheral")
    : deviceName(name), mode(mode), connected(false) {
       
    }

    void init_ble() {
        static bool bleInitialized = false;
        if (!bleInitialized) {
            Serial.println("[BLESimple] Initializing BLE");
            BLEDevice::init(deviceName.c_str());
            bleInitialized = true;
        }

        if (mode == "peripheral" && !pServer) {
            pServer = BLEDevice::createServer();
            pServer->setCallbacks(new ServerCallbacks(this));
        }
    }



    void start() {
        static bool bleInitialized = false;
        if (!bleInitialized) {
            Serial.println("[BLESimple] Initializing BLE");
            BLEDevice::init(deviceName.c_str());
            bleInitialized = true;
        }

        if (mode == "peripheral") {
            Serial.println("[BLESimple] Starting in Peripheral mode");
            if (!pServer) {
                pServer = BLEDevice::createServer();
                pServer->setCallbacks(new ServerCallbacks(this));
            }

            BLEAdvertising* pAdvertising = pServer->getAdvertising();
            for (auto const& [uuid, service] : services) {
                service->start();
                pAdvertising->addServiceUUID(uuid);
                Serial.printf("[BLESimple] Started service %s\n", uuid.c_str());
            }

            pAdvertising->start();
            Serial.println("[BLESimple] Advertising started");
        } else {
            Serial.println("[BLESimple] Starting in Central mode");
            pScan = BLEDevice::getScan();
            pClient = BLEDevice::createClient();
        }
    }

    void stop() {
        if (mode == "peripheral") {
            Serial.println("[BLESimple] Stopping advertising");
            if (pServer && pServer->getAdvertising())
                pServer->getAdvertising()->stop();
        } else if (connected) {
            Serial.println("[BLESimple] Disconnecting client");
            if (pClient) pClient->disconnect();
        }
        connected = false;
    }

    PyList<String> scan(int timeout) {
        PyList<String> results;
        if (!pScan) {
            Serial.println("[BLESimple] BLE Scan not initialized!");
            return results;
        }
        Serial.printf("[BLESimple] Starting BLE scan for %d seconds\n", timeout);
        BLEScanResults foundDevices = pScan->start(timeout, false);
        for (int i = 0; i < foundDevices.getCount(); ++i) {
            BLEAdvertisedDevice d = foundDevices.getDevice(i);
            if (d.haveName()) {
                String nameCopy = d.getName().c_str();
                Serial.printf("[BLESimple] Found device: %s\n", nameCopy.c_str());
                results.append(nameCopy);
            }
        }
        return results;
    }

    void add_service(const String& uuid) {
        if (mode == "peripheral") {
            Serial.printf("[BLESimple] Adding service UUID: %s\n", uuid.c_str());

            if (!pServer) {
                Serial.println("[DEBUG] pServer is NULL, creating...");
                pServer = BLEDevice::createServer();
                pServer->setCallbacks(new ServerCallbacks(this));
            }

            Serial.println("[DEBUG] Creating service...");
            BLEService* s = pServer->createService(uuid.c_str());

            if (!s) {
                Serial.println("[ERROR] Failed to create service!");
                return;
            }

            services[uuid.c_str()] = s;
            Serial.println("[DEBUG] Service created and stored.");
        }
    }


    void add_characteristic(const String& service_uuid, const String& char_uuid, const String& value = "", bool readable = true, bool writable = false, bool notify = false) {
        auto it = services.find(service_uuid.c_str());
        if (it == services.end()) {
            Serial.printf("[BLESimple] Service %s not found\n", service_uuid.c_str());
            return;
        }
        BLEService* service = it->second;
        Serial.printf("[BLESimple] Adding characteristic UUID: %s to service %s\n", char_uuid.c_str(), service_uuid.c_str());

        uint32_t props = 0;
        if (readable) props |= BLECharacteristic::PROPERTY_READ;
        if (writable) props |= BLECharacteristic::PROPERTY_WRITE;
        if (notify) props |= BLECharacteristic::PROPERTY_NOTIFY;

        BLECharacteristic* pChar = service->createCharacteristic(char_uuid.c_str(), props);
        pChar->setValue(value.c_str());
        pChar->setCallbacks(new CharacteristicCallbacks(this, char_uuid.c_str()));
        createdCharacteristics.append(pChar);
    }

    void on_write(const String& uuid, void (*callback)(String)) {
        Serial.printf("[BLESimple] Registered on_write callback for UUID: %s\n", uuid.c_str());
        writeCallbacks[uuid.c_str()] = callback;
    }

    // remaining methods unchanged...
};

void (*BLESimple::onConnectCallback)() = nullptr;
void (*BLESimple::onDisconnectCallback)() = nullptr;

#endif