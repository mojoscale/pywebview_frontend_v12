#ifndef PYDICT_H
#define PYDICT_H

#include <Arduino.h>
#include <ArduinoJson.h>
#include <type_traits>

// Forward declaration for PyDictItems
template<typename T>
class PyDictItems;

class PyInt;
class PyFloat;
class PyBool;
class PyString;

template<typename T>
class PyDict {
private:
    struct Entry {
        String key;
        T value;
        bool occupied;
    };

    Entry* data;
    int capacity;
    int length;

    void resize(int new_capacity) {
        Entry* old_data = data;
        int old_capacity = capacity;

        capacity = new_capacity;
        data = new Entry[capacity];
        for (int i = 0; i < capacity; i++) data[i].occupied = false;
        length = 0;

        for (int i = 0; i < old_capacity; i++) {
            if (old_data[i].occupied) {
                set(old_data[i].key, old_data[i].value);
            }
        }

        delete[] old_data;
    }

    int find_index(const String& key) const {
        for (int i = 0; i < capacity; i++) {
            if (data[i].occupied && data[i].key == key) return i;
        }
        return -1;
    }

    static constexpr bool is_allowed_type() {
        return std::is_same<T, int>::value ||
               std::is_same<T, float>::value ||
               std::is_same<T, bool>::value ||
               std::is_same<T, String>::value ||
               std::is_same<T, PyInt>::value ||
               std::is_same<T, PyFloat>::value ||
               std::is_same<T, PyBool>::value ||
               std::is_same<T, PyString>::value;
    }

public:
    PyDict() {
        static_assert(is_allowed_type(), "Only int, float, bool, String, or Py* types allowed in PyDict.");
        capacity = 8;
        length = 0;
        data = new Entry[capacity];
        for (int i = 0; i < capacity; i++) data[i].occupied = false;
    }

    PyDict(std::initializer_list<std::pair<String, T>> init_list) : PyDict() {
        for (auto& p : init_list) {
            set(p.first, p.second);
        }
    }

    PyDict(const String& json_str) : PyDict() {
        from_json(json_str);
    }

    // ✅ Copy constructor
    PyDict(const PyDict<T>& other) {
        capacity = other.capacity;
        length = other.length;
        data = new Entry[capacity];
        for (int i = 0; i < capacity; ++i) {
            data[i] = other.data[i];
        }
    }

    // ✅ Copy assignment
    PyDict& operator=(const PyDict<T>& other) {
        if (this != &other) {
            delete[] data;
            capacity = other.capacity;
            length = other.length;
            data = new Entry[capacity];
            for (int i = 0; i < capacity; ++i) {
                data[i] = other.data[i];
            }
        }
        return *this;
    }

    // ✅ Move constructor
    PyDict(PyDict<T>&& other) noexcept {
        capacity = other.capacity;
        length = other.length;
        data = other.data;
        other.data = nullptr;
        other.capacity = 0;
        other.length = 0;
    }

    // ✅ Move assignment
    PyDict& operator=(PyDict<T>&& other) noexcept {
        if (this != &other) {
            delete[] data;
            capacity = other.capacity;
            length = other.length;
            data = other.data;
            other.data = nullptr;
            other.capacity = 0;
            other.length = 0;
        }
        return *this;
    }

    ~PyDict() {
        delete[] data;
    }

    void set(const String& key, T value) {
        int idx = find_index(key);
        if (idx != -1) {
            data[idx].value = value;
            return;
        }

        if (length >= capacity * 0.7) {
            resize(capacity * 2);
        }

        for (int i = 0; i < capacity; i++) {
            if (!data[i].occupied) {
                data[i].key = key;
                data[i].value = value;
                data[i].occupied = true;
                length++;
                return;
            }
        }
    }

    T get(const String& key) const {
        int idx = find_index(key);
        if (idx == -1) {
            Serial.println("KeyError: key not found");
            return T();
        }
        return data[idx].value;
    }

    T get(const String& key, const T& default_val) const {
        int idx = find_index(key);
        return (idx == -1) ? default_val : data[idx].value;
    }

    T& operator[](const String& key) {
        int idx = find_index(key);
        if (idx == -1) {
            set(key, T());
            idx = find_index(key);
        }
        return data[idx].value;
    }

    PyDictItems<T> items() const {
        return PyDictItems<T>(*this);
    }

    bool operator==(const PyDict<T>& other) const {
        if (length != other.size()) return false;
        for (int i = 0; i < capacity; ++i) {
            if (data[i].occupied) {
                if (!other.contains(data[i].key)) return false;
                if (!(data[i].value == other.get(data[i].key))) return false;
            }
        }
        return true;
    }

    void remove(const String& key) {
        int idx = find_index(key);
        if (idx == -1) {
            Serial.println("KeyError: key not found");
            return;
        }
        data[idx].occupied = false;
        length--;
    }

    T pop(const String& key) {
        int idx = find_index(key);
        if (idx == -1) {
            Serial.println("KeyError: pop(): key not found");
            return T();
        }
        T val = data[idx].value;
        data[idx].occupied = false;
        length--;
        return val;
    }

    bool contains(const String& key) const {
        return find_index(key) != -1;
    }

    void clear() {
        delete[] data;
        capacity = 8;
        length = 0;
        data = new Entry[capacity];
        for (int i = 0; i < capacity; i++) data[i].occupied = false;
    }

    int size() const {
        return length;
    }

    bool is_empty() const {
        return length == 0;
    }

    void update(const PyDict<T>& other) {
        for (int i = 0; i < other.capacity; ++i) {
            if (other.data[i].occupied) {
                set(other.data[i].key, other.data[i].value);
            }
        }
    }

    PyDict<T> copy() const {
        PyDict<T> result;
        result = *this;
        return result;
    }

    T setdefault(const String& key, const T& default_val) {
        int idx = find_index(key);
        if (idx != -1) return data[idx].value;
        set(key, default_val);
        return default_val;
    }

    static PyDict<T> fromkeys(const PyList<String>& keys, const T& value) {
        PyDict<T> result;
        for (size_t i = 0; i < keys.size(); ++i) {
            result.set(keys[i], value);
        }
        return result;
    }

    PyList<String> keys() const {
        PyList<String> result;
        for (int i = 0; i < capacity; ++i) {
            if (data[i].occupied) {
                result.append(data[i].key);
            }
        }
        return result;
    }

    PyList<T> values() const {
        PyList<T> result;
        for (int i = 0; i < capacity; ++i) {
            if (data[i].occupied) {
                result.append(data[i].value);
            }
        }
        return result;
    }

    String key_at(int index) const {
        int count = 0;
        for (int i = 0; i < capacity; ++i) {
            if (data[i].occupied) {
                if (count == index) return data[i].key;
                count++;
            }
        }
        Serial.println("IndexError: dict index out of range");
        return "";
    }

    void from_json(const String& json_str); // specializations elsewhere

    String to_json() const {
        ArduinoJson::DynamicJsonDocument doc(512);
        for (int i = 0; i < capacity; ++i) {
            if (data[i].occupied) {
                doc[data[i].key] = data[i].value;
            }
        }
        String output;
        serializeJson(doc, output);
        return output;
    }

    void print() const {
        Serial.println(to_json());
    }

    String to_string() const {
        String result = "{";
        bool first = true;
        for (int i = 0; i < capacity; ++i) {
            if (data[i].occupied) {
                if (!first) result += ", ";
                first = false;
                result += "\"" + data[i].key + "\": ";

                if constexpr (std::is_same<T, bool>::value) {
                    result += data[i].value ? "True" : "False";
                } else if constexpr (std::is_same<T, int>::value || std::is_same<T, float>::value) {
                    result += String(data[i].value);
                } else if constexpr (std::is_same<T, String>::value) {
                    result += "\"" + data[i].value + "\"";
                } else {
                    result += data[i].value.to_string();
                }
            }
        }
        result += "}";
        return result;
    }
};

#endif
