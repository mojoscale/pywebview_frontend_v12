

#include <OneWire.h>
#include "../PyList.h"

PyList<int> custom_onewire_helper_read_bytes(OneWire& wire, int count) {
    uint8_t buf[count];
    wire.read_bytes(buf, count);

    PyList<int> result;
    for (int i = 0; i < count; ++i) {
        result.append(static_cast<int>(buf[i]));
    }
    return result;
}


PyList<int> custom_onewire_helper_search(OneWire& wire) {
    uint8_t addr[8];
    bool found = wire.search(addr);

    if (!found) {
        return PyList<int>();  // Return empty list
    }

    PyList<int> rom;
    for (int i = 0; i < 8; ++i) {
        rom.append(static_cast<int>(addr[i]));
    }
    return rom;
}
