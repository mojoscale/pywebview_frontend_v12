#include <ArduinoJson.h>

// Extracts "value" field from a JSON string.
// Returns an empty string if key not found or JSON invalid.
String getValueFromJson(const String& jsonStr) {
  DynamicJsonDocument doc(256);

  DeserializationError err = deserializeJson(doc, jsonStr);
  if (err) {
    Serial.print("JSON parse error: ");
    Serial.println(err.c_str());
    return "";
  }

  if (!doc.containsKey("value")) return "";

  return doc["value"].as<String>();
}
