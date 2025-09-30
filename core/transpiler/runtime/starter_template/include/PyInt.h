#ifndef PYINT_H
#define PYINT_H

#include <Arduino.h>

class PyInt {
private:
    long value;

public:
    // Constructors
    PyInt() : value(0) {}
    PyInt(int v) : value(v) {}
    PyInt(long v) : value(v) {}

    // ✅ Copy constructor
    PyInt(const PyInt& other) : value(other.value) {}

    // ✅ Copy assignment
    PyInt& operator=(const PyInt& other) {
        if (this != &other) {
            value = other.value;
        }
        return *this;
    }

    // ✅ Move constructor
    PyInt(PyInt&& other) noexcept : value(other.value) {}

    // ✅ Move assignment
    PyInt& operator=(PyInt&& other) noexcept {
        if (this != &other) {
            value = other.value;
        }
        return *this;
    }

    // Getter
    long get() const {
        return value;
    }

    // Arithmetic
    PyInt operator+(const PyInt& other) const {
        return PyInt(value + other.value);
    }

    PyInt operator-(const PyInt& other) const {
        return PyInt(value - other.value);
    }

    PyInt operator*(const PyInt& other) const {
        return PyInt(value * other.value);
    }

    PyInt operator/(const PyInt& other) const {
        return PyInt(value / other.value);
    }

    PyInt operator%(const PyInt& other) const {
        return PyInt(value % other.value);
    }

    PyInt pow(PyInt exponent) const {
        long result = 1;
        long base = value;
        long exp = exponent.value;
        for (int i = 0; i < exp; ++i) {
            result *= base;
        }
        return PyInt(result);
    }

    PyInt operator-() const {
        return PyInt(-value);
    }

    // Comparisons
    bool operator==(const PyInt& other) const {
        return value == other.value;
    }

    bool operator!=(const PyInt& other) const {
        return value != other.value;
    }

    bool operator<(const PyInt& other) const {
        return value < other.value;
    }

    bool operator<=(const PyInt& other) const {
        return value <= other.value;
    }

    bool operator>(const PyInt& other) const {
        return value > other.value;
    }

    bool operator>=(const PyInt& other) const {
        return value >= other.value;
    }

    // Bitwise-style
    int bit_length() const {
        unsigned long v = value < 0 ? -value : value;
        int bits = 0;
        while (v) {
            bits++;
            v >>= 1;
        }
        return bits;
    }

    int bit_count() const {
        unsigned long v = value < 0 ? -value : value;
        int count = 0;
        while (v) {
            count += v & 1;
            v >>= 1;
        }
        return count;
    }

    // Numeric info
    int numerator() const {
        return value;
    }

    int denominator() const {
        return 1;
    }

    bool is_integer() const {
        return true;
    }

    long real() const {
        return value;
    }

    long imag() const {
        return 0;
    }

    PyInt conjugate() const {
        return *this;
    }

    void as_integer_ratio(long& num, long& denom) const {
        num = value;
        denom = 1;
    }

    // Binary conversions
    String to_bytes() const {
        String s = "";
        for (int i = sizeof(long) - 1; i >= 0; --i) {
            s += (char)((value >> (i * 8)) & 0xFF);
        }
        return s;
    }

    static PyInt from_bytes(const String& s) {
        long val = 0;
        for (size_t i = 0; i < s.length(); ++i) {
            val = (val << 8) | (unsigned char)s[i];
        }
        return PyInt(val);
    }

    // Display
    void print() const {
        Serial.print(value);
    }

    // Implicit cast
    operator long() const {
        return value;
    }
};

#endif
