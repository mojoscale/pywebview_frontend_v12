#ifndef MQTT_CONNECT_HELPER_H
#define MQTT_CONNECT_HELPER_H

#include <Arduino.h>
#include <PubSubClient.h>




// Global pointer to store the user's callback
void (*userStringCallback)(String, String) = nullptr;

// Internal callback that handles the conversion
void internalCallback(char* topic, byte* payload, unsigned int length) {
    if (userStringCallback) {
        // Convert to Strings for user
        String topicStr = String(topic);
        String payloadStr;
        for (unsigned int i = 0; i < length; i++) {
            payloadStr += (char)payload[i];
        }
        // Call user's simple callback
        userStringCallback(topicStr, payloadStr);
    }
}

// Your wrapper function
void setupSimpleCallback(PubSubClient& client, void (*callback)(String, String)) {
    userStringCallback = callback;
    client.setCallback(internalCallback);
}



/**
 * Unified MQTT connect helper for PubSubClient.
 *
 * This function provides a single entry point for all connect variants:
 *  - client_id only
 *  - client_id + auth
 *  - client_id + last will
 *  - client_id + auth + last will
 *
 * It detects which parameters are non-empty and calls the corresponding
 * PubSubClient::connect() overload automatically.
 *
 * @param client        Reference to an existing PubSubClient instance
 * @param client_id     MQTT client identifier
 * @param username      (optional) Username for authentication
 * @param password      (optional) Password for authentication
 * @param will_topic    (optional) Last Will topic
 * @param will_qos      QoS level for last will (0–2)
 * @param will_retain   Whether the last will message should be retained
 * @param will_message  (optional) Message for the last will topic
 *
 * @return true if connection succeeded, false otherwise
 */
bool custom_mqtt_connect(
    PubSubClient& client,
    const String& client_id,
    const String& username = "",
    const String& password = "",
    const String& will_topic = "",
    int will_qos = 0,
    bool will_retain = false,
    const String& will_message = ""
) {
    // ---- CASE 1: Simple connect ----
    if (username.isEmpty() && will_topic.isEmpty()) {
        return client.connect(client_id.c_str());
    }

    // ---- CASE 2: Auth only ----
    if (!username.isEmpty() && will_topic.isEmpty()) {
        return client.connect(client_id.c_str(),
                              username.c_str(),
                              password.c_str());
    }

    // ---- CASE 3: Will only ----
    if (username.isEmpty() && !will_topic.isEmpty()) {
        return client.connect(client_id.c_str(),
                              will_topic.c_str(),
                              will_qos,
                              will_retain,
                              will_message.c_str());
    }

    // ---- CASE 4: Auth + Will ----
    return client.connect(client_id.c_str(),
                          username.c_str(),
                          password.c_str(),
                          will_topic.c_str(),
                          will_qos,
                          will_retain,
                          will_message.c_str());
}

#endif  // MQTT_CONNECT_HELPER_H