#ifndef PYDICT_FROM_JSON_SPECIALIZATIONS_H
#define PYDICT_FROM_JSON_SPECIALIZATIONS_H

#include <ArduinoJson.h>
#include "PyDict.h"
#include "PyInt.h"
#include "PyFloat.h"
#include "PyBool.h"
#include "PyString.h"

template<>
inline void PyDict<int>::from_json(const String& json_str) {
    ArduinoJson::DynamicJsonDocument doc(512);
    auto err = deserializeJson(doc, json_str);
    if (err) {
        Serial.print("JSON parse error: ");
        Serial.println(err.f_str());
        return;
    }
    for (JsonPair kv : doc.as<JsonObject>()) {
        set(kv.key().c_str(), kv.value().as<int>());
    }
}

template<>
inline void PyDict<float>::from_json(const String& json_str) {
    ArduinoJson::DynamicJsonDocument doc(512);
    auto err = deserializeJson(doc, json_str);
    if (err) {
        Serial.print("JSON parse error: ");
        Serial.println(err.f_str());
        return;
    }
    for (JsonPair kv : doc.as<JsonObject>()) {
        set(kv.key().c_str(), kv.value().as<float>());
    }
}

template<>
inline void PyDict<bool>::from_json(const String& json_str) {
    ArduinoJson::DynamicJsonDocument doc(512);
    auto err = deserializeJson(doc, json_str);
    if (err) {
        Serial.print("JSON parse error: ");
        Serial.println(err.f_str());
        return;
    }
    for (JsonPair kv : doc.as<JsonObject>()) {
        set(kv.key().c_str(), kv.value().as<bool>());
    }
}

template<>
inline void PyDict<String>::from_json(const String& json_str) {
    ArduinoJson::DynamicJsonDocument doc(512);
    auto err = deserializeJson(doc, json_str);
    if (err) {
        Serial.print("JSON parse error: ");
        Serial.println(err.f_str());
        return;
    }
    for (JsonPair kv : doc.as<JsonObject>()) {
        set(kv.key().c_str(), kv.value().as<String>());
    }
}

template<>
inline void PyDict<PyInt>::from_json(const String& json_str) {
    ArduinoJson::DynamicJsonDocument doc(512);
    auto err = deserializeJson(doc, json_str);
    if (err) {
        Serial.print("JSON parse error: ");
        Serial.println(err.f_str());
        return;
    }
    for (JsonPair kv : doc.as<JsonObject>()) {
        set(kv.key().c_str(), PyInt(kv.value().as<int>()));
    }
}

template<>
inline void PyDict<PyFloat>::from_json(const String& json_str) {
    ArduinoJson::DynamicJsonDocument doc(512);
    auto err = deserializeJson(doc, json_str);
    if (err) {
        Serial.print("JSON parse error: ");
        Serial.println(err.f_str());
        return;
    }
    for (JsonPair kv : doc.as<JsonObject>()) {
        set(kv.key().c_str(), PyFloat(kv.value().as<float>()));
    }
}

template<>
inline void PyDict<PyBool>::from_json(const String& json_str) {
    ArduinoJson::DynamicJsonDocument doc(512);
    auto err = deserializeJson(doc, json_str);
    if (err) {
        Serial.print("JSON parse error: ");
        Serial.println(err.f_str());
        return;
    }
    for (JsonPair kv : doc.as<JsonObject>()) {
        set(kv.key().c_str(), PyBool(kv.value().as<bool>()));
    }
}

template<>
inline void PyDict<PyString>::from_json(const String& json_str) {
    ArduinoJson::DynamicJsonDocument doc(512);
    auto err = deserializeJson(doc, json_str);
    if (err) {
        Serial.print("JSON parse error: ");
        Serial.println(err.f_str());
        return;
    }
    for (JsonPair kv : doc.as<JsonObject>()) {
        set(kv.key().c_str(), PyString(kv.value().as<String>()));
    }
}

#endif // PYDICT_FROM_JSON_SPECIALIZATIONS_H
