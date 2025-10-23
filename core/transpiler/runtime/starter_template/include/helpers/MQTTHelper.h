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