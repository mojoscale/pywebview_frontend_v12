#ifndef PYFLOAT_H
#define PYFLOAT_H

#include <Arduino.h>
#include <math.h>
#include <utility>
#include <PyList.h>

class PyFloat {
private:
    double value;

public:
    // Constructors
    PyFloat() : value(0.0) {}
    PyFloat(float v) : value(v) {}
    PyFloat(double v) : value(v) {}

    // ✅ Copy constructor
    PyFloat(const PyFloat& other) : value(other.value) {}

    // ✅ Copy assignment
    PyFloat& operator=(const PyFloat& other) {
        if (this != &other) {
            value = other.value;
        }
        return *this;
    }

    // ✅ Move constructor
    PyFloat(PyFloat&& other) noexcept : value(other.value) {}

    // ✅ Move assignment
    PyFloat& operator=(PyFloat&& other) noexcept {
        if (this != &other) {
            value = other.value;
        }
        return *this;
    }

    // Accessor
    double get() const {
        return value;
    }

    // Arithmetic operators
    PyFloat operator+(const PyFloat& other) const {
        return PyFloat(value + other.value);
    }

    PyFloat operator-(const PyFloat& other) const {
        return PyFloat(value - other.value);
    }

    PyFloat operator*(const PyFloat& other) const {
        return PyFloat(value * other.value);
    }

    PyFloat operator/(const PyFloat& other) const {
        return PyFloat(value / other.value);
    }

    PyFloat operator%(const PyFloat& other) const {
        return PyFloat(fmod(value, other.value));
    }

    PyFloat operator-() const {
        return PyFloat(-value);
    }

    // Comparisons
    bool operator==(const PyFloat& other) const {
        return fabs(value - other.value) < 1e-6;
    }

    bool operator!=(const PyFloat& other) const {
        return !(*this == other);
    }

    bool operator<(const PyFloat& other) const {
        return value < other.value;
    }

    bool operator<=(const PyFloat& other) const {
        return value <= other.value;
    }

    bool operator>(const PyFloat& other) const {
        return value > other.value;
    }

    bool operator>=(const PyFloat& other) const {
        return value >= other.value;
    }

    // Python-style methods
    float pow(PyFloat exponent) const {
        return powf(value, exponent.get());
    }
    
    bool is_integer() const {
        return floor(value) == value;
    }

    PyList<int> as_integer_ratio() const {
        double frac = value;
        long n = 1;

        while (floor(frac) != frac && n < 1000000) {
            frac *= 10.0;
            n *= 10;
        }

        long num = static_cast<long>(frac);
        long denom = n;

        // Construct a PyList<int> with two elements
        PyList<int> result = PyList<int>::from({ static_cast<int>(num),
                                                 static_cast<int>(denom) });
        return result;
    }


    String hex() const {
        char buf[32];
        dtostrf(value, 0, 6, buf);
        return String(buf);
    }

    long round() const {
        return (long)(value >= 0 ? value + 0.5 : value - 0.5);
    }

    void print(int digits = 6) const {
        Serial.print(value, digits);
    }

    String str(int digits = 6) const {
        char buf[32];
        dtostrf(value, 0, digits, buf);
        return String(buf);
    }

    String real() const {
        return str();
    }

    String imag() const {
        return "0";
    }

    float conjugate() const {
        return static_cast<float>(value);
    }


    int bit_length() const {
        long int_val = static_cast<long>(fabs(value));
        int count = 0;
        while (int_val > 0) {
            int_val >>= 1;
            count++;
        }
        return count;
    }

    int bit_count() const {
        long int_val = static_cast<long>(fabs(value));
        int count = 0;
        while (int_val) {
            count += int_val & 1;
            int_val >>= 1;
        }
        return count;
    }

    String to_bytes() const {
        char buf[sizeof(double)];
        memcpy(buf, &value, sizeof(double));
        return String(buf);
    }

    static PyFloat from_bytes(const String& s) {
        if (s.length() < (int)sizeof(double)) return PyFloat(0.0);
        double val;
        memcpy(&val, s.c_str(), sizeof(double));
        return PyFloat(val);
    }

    // Implicit conversion
    operator double() const {
        return value;
    }
};

#endif
