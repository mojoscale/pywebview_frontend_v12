#ifndef ONEWIRE_H
#define ONEWIRE_H

#include <Arduino.h>
class OneWire {
public:
  OneWire(uint8_t pin);
  bool search(uint8_t *newAddr);
  void reset_search(void);
  bool reset(void);
  void write(uint8_t v, uint8_t power = 0);
  void write_bytes(const uint8_t *buf, uint8_t count, bool power = false);
  uint8_t read(void);
  void read_bytes(uint8_t *buf, uint8_t count);
  void select(const uint8_t *rom);
  void skip(void);
};
#endif
