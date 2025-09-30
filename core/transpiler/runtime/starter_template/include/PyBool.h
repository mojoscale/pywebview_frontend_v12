#ifndef PYBOOL_H
#define PYBOOL_H

#include <Arduino.h>

class PyBool {
private:
    bool value;

public:
    // Constructors
    PyBool() : value(false) {}
    PyBool(bool v) : value(v) {}
    PyBool(int v) : value(v != 0) {}

    // ✅ Copy constructor
    PyBool(const PyBool& other) : value(other.value) {}

    // ✅ Copy assignment
    PyBool& operator=(const PyBool& other) {
        if (this != &other) {
            value = other.value;
        }
        return *this;
    }

    // ✅ Move constructor
    PyBool(PyBool&& other) noexcept : value(other.value) {}

    // ✅ Move assignment
    PyBool& operator=(PyBool&& other) noexcept {
        if (this != &other) {
            value = other.value;
        }
        return *this;
    }

    // Logical operators
    PyBool operator!() const {
        return PyBool(!value);
    }

    bool operator==(const PyBool& other) const {
        return value == other.value;
    }

    bool operator!=(const PyBool& other) const {
        return value != other.value;
    }

    PyBool operator&&(const PyBool& other) const {
        return PyBool(value && other.value);
    }

    PyBool operator||(const PyBool& other) const {
        return PyBool(value || other.value);
    }

    // Conversion
    operator bool() const {
        return value;
    }

    bool get() const {
        return value;
    }

    void toggle() {
        value = !value;
    }

    // Display
    void print() const {
        Serial.print(value ? "True" : "False");
    }

    String str() const {
        return value ? "True" : "False";
    }

    String to_string() const {
        return value ? "True" : "False";
    }

    static PyBool fromString(const String& s) {
        return PyBool(s == "True" || s == "true" || s == "1");
    }

    // Python-style extras
    int bit_length() const {
        return value ? 1 : 0;
    }

    int bit_count() const {
        return value ? 1 : 0;
    }

    int numerator() const {
        return value ? 1 : 0;
    }

    int denominator() const {
        return 1;
    }

    bool is_integer() const {
        return true;
    }

    String real() const {
        return str();
    }

    String imag() const {
        return "0";
    }

    PyBool conjugate() const {
        return *this;
    }

    void as_integer_ratio(long& num, long& denom) const {
        num = value ? 1 : 0;
        denom = 1;
    }

    String to_bytes() const {
        return String((char)(value ? 1 : 0));
    }

    static PyBool from_bytes(const String& s) {
        return PyBool(s.length() > 0 && s[0] != 0);
    }
};

#endif
