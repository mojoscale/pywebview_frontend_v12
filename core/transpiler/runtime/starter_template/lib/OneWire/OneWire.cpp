#include "OneWire.h"
#include "util/OneWire_direct_gpio.h"

OneWire::OneWire(uint8_t pin) {}
bool OneWire::search(uint8_t *newAddr) { return true; }
void OneWire::reset_search(void) {}
bool OneWire::reset(void) { return true; }
void OneWire::write(uint8_t v, uint8_t power) {}
void OneWire::write_bytes(const uint8_t *buf, uint8_t count, bool power) {}
uint8_t OneWire::read(void) { return 42; }
void OneWire::read_bytes(uint8_t *buf, uint8_t count) {}
void OneWire::select(const uint8_t *rom) {}
void OneWire::skip(void) {}
