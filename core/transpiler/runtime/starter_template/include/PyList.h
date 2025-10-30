#ifndef PYLIST_H
#define PYLIST_H

#include <Arduino.h>
#include <type_traits>
#include <PyInt.h>
#include <PyBool.h>

class PyString;  // Forward declare

class PyFloat;   // ✅ Add forward declare



template<typename T>
class PyList {
private:
    T* data;
    int capacity;
    int length;

    void resize(int new_capacity) {
        T* new_data = new T[new_capacity];
        for (int i = 0; i < length; i++) {
            new_data[i] = data[i];
        }
        delete[] data;
        data = new_data;
        capacity = new_capacity;
    }

    static String format_item(const T& item) {
        if (std::is_same<T, String>::value) {
            return "\"" + item + "\"";
        }
        if (std::is_same<T, bool>::value) {
            return item ? "True" : "False";
        }
        if (std::is_same<T, PyInt>::value ||
            std::is_same<T, PyFloat>::value ||
            std::is_same<T, PyBool>::value ||
            std::is_same<T, PyString>::value) {
            item.print();  // Already prints to Serial
            return "";
        }
        return String(item);  // fallback
    }

public:
    PyList() {
        capacity = 4;
        length = 0;
        data = new T[capacity];
    }

    PyList(T arr[], int size) {
        capacity = size * 2;
        length = size;
        data = new T[capacity];
        for (int i = 0; i < size; i++) {
            data[i] = arr[i];
        }
    }

    PyList(std::initializer_list<T> items) {
        length = capacity = items.size();
        data = new T[capacity];
        int i = 0;
        for (const auto& item : items) {
            data[i++] = item;
        }
    }

    // ✅ Copy constructor
    PyList(const PyList<T>& other) {
        capacity = other.capacity;
        length = other.length;
        data = new T[capacity];
        for (int i = 0; i < length; ++i) {
            data[i] = other.data[i];
        }
    }

    // ✅ Copy assignment
    PyList<T>& operator=(const PyList<T>& other) {
        if (this != &other) {
            delete[] data;
            capacity = other.capacity;
            length = other.length;
            data = new T[capacity];
            for (int i = 0; i < length; ++i) {
                data[i] = other.data[i];
            }
        }
        return *this;
    }

    // ✅ Move constructor
    PyList(PyList<T>&& other) noexcept {
        data = other.data;
        capacity = other.capacity;
        length = other.length;
        other.data = nullptr;
        other.capacity = 0;
        other.length = 0;
    }

    // ✅ Move assignment
    PyList<T>& operator=(PyList<T>&& other) noexcept {
        if (this != &other) {
            delete[] data;
            data = other.data;
            capacity = other.capacity;
            length = other.length;
            other.data = nullptr;
            other.capacity = 0;
            other.length = 0;
        }
        return *this;
    }

    static PyList<T> from(std::initializer_list<T> items) {
        return PyList<T>(items);
    }

    ~PyList() {
        delete[] data;
    }

    void append(T value) {
        if (length >= capacity) resize(capacity * 2);
        data[length++] = value;
    }

    T pop() {
        if (length == 0) {
            Serial.println("IndexError: pop from empty list");
            return T();
        }
        return data[--length];
    }

    void insert(int index, T value) {
        if (index < 0 || index > length) {
            Serial.println("IndexError: insert index out of range");
            return;
        }
        if (length >= capacity) resize(capacity * 2);
        for (int i = length; i > index; i--) {
            data[i] = data[i - 1];
        }
        data[index] = value;
        length++;
    }

    bool contains(const T& value) const {
        for (int i = 0; i < length; ++i) {
            if (data[i] == value) return true;
        }
        return false;
    }

    void remove(T value) {
        for (int i = 0; i < length; i++) {
            if (data[i] == value) {
                for (int j = i; j < length - 1; j++) {
                    data[j] = data[j + 1];
                }
                length--;
                return;
            }
        }
        Serial.println("ValueError: value not found in list");
    }

    int index(T value) {
        for (int i = 0; i < length; i++) {
            if (data[i] == value) return i;
        }
        Serial.println("ValueError: value not in list");
        return -1;
    }

    int count(T value) const {
        int cnt = 0;
        for (int i = 0; i < length; ++i) {
            if (data[i] == value) cnt++;
        }
        return cnt;
    }

    void set(int index, T value) {
        if (index < 0 || index >= length) {
            Serial.println("IndexError: list assignment index out of range");
            return;
        }
        data[index] = value;
    }

    void set(const PyInt& index, T value) {
        set(index.get(), value);
    }

    int size() const {
        return length;
    }

    T& operator[](int index) {
        if (index < 0 || index >= length) {
            Serial.println("IndexError: list index out of range");
            static T dummy;
            return dummy;
        }
        return data[index];
    }

    const T& operator[](int index) const {
        if (index < 0 || index >= length) {
            Serial.println("IndexError: list index out of range");
            static T dummy;
            return dummy;
        }
        return data[index];
    }

    T& operator[](const PyInt& index) {
        return (*this)[index.get()];
    }

    const T& operator[](const PyInt& index) const {
        return (*this)[index.get()];
    }

    PyList<T> operator+(const PyList<T>& other) const {
        PyList<T> result;
        result.extend(*this);
        result.extend(other);
        return result;
    }

    PyList<T> operator-(const PyList<T>& other) const {
        PyList<T> result;
        for (int i = 0; i < this->size(); ++i) {
            bool found = false;
            for (int j = 0; j < other.size(); ++j) {
                if (data[i] == other[j]) {
                    found = true;
                    break;
                }
            }
            if (!found) result.append(data[i]);
        }
        return result;
    }

    PyList<T> operator*(int times) const {
        PyList<T> result;
        for (int i = 0; i < times; ++i) {
            result.extend(*this);
        }
        return result;
    }

    PyList<T> copy() const {
        PyList<T> result;
        for (int i = 0; i < length; ++i) {
            result.append(data[i]);
        }
        return result;
    }

    void clear() {
        length = 0;
    }

    void extend(const PyList<T>& other) {
        for (int i = 0; i < other.size(); ++i) {
            append(other[i]);
        }
    }

    void reverse() {
        for (int i = 0; i < length / 2; ++i) {
            T temp = data[i];
            data[i] = data[length - i - 1];
            data[length - i - 1] = temp;
        }
    }

    void sort(bool reverse = false) {
        for (int i = 0; i < length - 1; ++i) {
            for (int j = 0; j < length - i - 1; ++j) {
                if ((reverse && data[j] < data[j + 1]) || (!reverse && data[j] > data[j + 1])) {
                    T temp = data[j];
                    data[j] = data[j + 1];
                    data[j + 1] = temp;
                }
            }
        }
    }

    bool operator==(const PyList<T>& other) const {
        if (length != other.size()) return false;
        for (int i = 0; i < length; ++i) {
            if (data[i] != other[i]) return false;
        }
        return true;
    }

    PyList<T> slice(int start, int end) const {
        PyList<T> result;
        if (start < 0) start = 0;
        if (end > length) end = length;
        for (int i = start; i < end; ++i) {
            result.append(data[i]);
        }
        return result;
    }

    void print() {
        Serial.print("[");
        for (int i = 0; i < length; ++i) {
            if (std::is_same<T, PyInt>::value ||
                std::is_same<T, PyFloat>::value ||
                std::is_same<T, PyBool>::value ||
                std::is_same<T, PyString>::value) {
                data[i].print();
            } else {
                Serial.print(format_item(data[i]));
            }
            if (i < length - 1) Serial.print(", ");
        }
        Serial.println("]");
    }

    String to_string() const {
        String result = "[";
        for (int i = 0; i < length; ++i) {
            if (i > 0) result += ", ";

            if constexpr (std::is_same<T, String>::value) {
                result += "\"" + data[i] + "\"";
            }
            else if constexpr (std::is_same<T, float>::value || 
                               std::is_same<T, double>::value || 
                               std::is_same<T, int>::value) {
                result += "\"" + String(data[i]) + "\"";
            }
            else if constexpr (std::is_same<T, bool>::value) {
                result += data[i] ? "True" : "False";
            }
            else if constexpr (std::is_same<T, PyInt>::value ||
                               std::is_same<T, PyFloat>::value ||
                               std::is_same<T, PyBool>::value ||
                               std::is_same<T, PyString>::value) {
                result += data[i].to_string();
            }
            else {
                result += String(data[i]);
            }
        }

        result += "]";
        return result;
    }
};

#endif
