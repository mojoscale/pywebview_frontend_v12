extern "C" void app_main() {
    // --------------------------------------------------
    // 0. Critical: DO NOT return from app_main
    // --------------------------------------------------
    printf("app_main started\n");
    printf("Initial free heap: %d\n", esp_get_free_heap_size());

    // --------------------------------------------------
    // 1. Initialize Arduino framework
    // --------------------------------------------------
    initArduino();

    Serial.begin(115200);
    delay(500);
    Serial.println("Arduino initialized from app_main");

    // --------------------------------------------------
    // 2. Protect against autostart conflict
    //    If autostart is ON, Arduino already created its
    //    own setup()/loop() task — creating another will
    //    fail. So detect and handle this.
    // --------------------------------------------------
#if CONFIG_AUTOSTART_ARDUINO
    Serial.println("WARNING: Autostart Arduino is ENABLED.");
    Serial.println("Using built-in Arduino loop task.");
    Serial.flush();

    // Prevent app_main from returning
    while (true) {
        vTaskDelay(pdMS_TO_TICKS(1000));
    }
#endif

    // --------------------------------------------------
    // 3. Create the custom Arduino loop task
    // --------------------------------------------------
    Serial.println("Creating custom Arduino task...");
    Serial.flush();

    BaseType_t result = xTaskCreatePinnedToCore(
        [](void*) {
            Serial.println("Arduino task STARTED");
            Serial.flush();

            try {
                setup();
                Serial.println("setup() DONE");
                Serial.flush();

                for (;;) {
                    loop();
                    delay(1);  // allow background tasks
                }

            } catch (...) {
                Serial.println("FATAL ERROR: Arduino task crashed");
                Serial.flush();
                while (true) {
                    vTaskDelay(pdMS_TO_TICKS(1000));
                }
            }
        },
        "arduino_task",
        24576,          // stack
        nullptr,        // parameter
        1,              // priority
        nullptr,        // handle
        APP_CPU_NUM     // core
    );

    // --------------------------------------------------
    // 4. Validate task creation
    // --------------------------------------------------
    if (result != pdPASS) {
        Serial.println("ERROR: xTaskCreatePinnedToCore FAILED!");
        Serial.printf("Free heap now: %d\n", esp_get_free_heap_size());
        Serial.println("System will halt so logs remain visible.");
        Serial.flush();

        while (true) {
            vTaskDelay(pdMS_TO_TICKS(1000));
        }
    }

    Serial.println("Arduino task CREATED successfully");
    Serial.flush();

    // --------------------------------------------------
    // 5. BLOCK FOREVER — do not return from app_main
    // --------------------------------------------------
    while (true) {
        vTaskDelay(pdMS_TO_TICKS(1000));
    }
}
