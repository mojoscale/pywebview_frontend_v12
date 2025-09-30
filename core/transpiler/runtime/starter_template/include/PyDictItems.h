#ifndef PYDICTITEMS_H
#define PYDICTITEMS_H

#include "PyDict.h"

template<typename T>
class PyDictItems {
private:
    const PyDict<T>& dict;

public:
    // Constructor
    PyDictItems(const PyDict<T>& d) : dict(d) {}

    // ✅ Copy constructor
    PyDictItems(const PyDictItems& other) : dict(other.dict) {}

    // ✅ Copy assignment
    PyDictItems& operator=(const PyDictItems& other) {
        if (this != &other) {
            // dict is a const reference, so nothing to reassign
        }
        return *this;
    }

    // ✅ Move constructor
    PyDictItems(PyDictItems&& other) noexcept : dict(other.dict) {}

    // ✅ Move assignment
    PyDictItems& operator=(PyDictItems&& other) noexcept {
        if (this != &other) {
            // dict is a const reference, so nothing to move
        }
        return *this;
    }

    int size() const {
        return dict.size();
    }

    String key_at(int index) const {
        return dict.key_at(index);
    }

    T value_at(int index) const {
        String key = dict.key_at(index);
        return dict.get(key);
    }

    struct Item {
        String key;
        T value;
    };

    Item get(int index) const {
        String key = dict.key_at(index);
        return { key, dict.get(key) };
    }

    String to_string() const {
        String result = "[";
        for (int i = 0; i < size(); ++i) {
            if (i > 0) result += ", ";
            String key_str = "\"" + key_at(i) + "\"";

            if constexpr (std::is_same<T, bool>::value) {
                result += "(" + key_str + ", " + (value_at(i) ? "True" : "False") + ")";
            } else if constexpr (std::is_same<T, int>::value || std::is_same<T, float>::value) {
                result += "(" + key_str + ", " + String(value_at(i)) + ")";
            } else if constexpr (std::is_same<T, String>::value) {
                result += "(" + key_str + ", \"" + value_at(i) + "\")";
            } else {
                result += "(" + key_str + ", " + value_at(i).to_string() + ")";
            }
        }
        result += "]";
        return result;
    }

    // Nested iterator class
    class Iterator {
    private:
        const PyDictItems<T>& items;
        int index;

    public:
        Iterator(const PyDictItems<T>& items, int index)
            : items(items), index(index) {}

        bool operator!=(const Iterator& other) const {
            return index != other.index;
        }

        Item operator*() const {
            return items.get(index);
        }

        const Iterator& operator++() {
            ++index;
            return *this;
        }
    };

    Iterator begin() const { return Iterator(*this, 0); }
    Iterator end() const { return Iterator(*this, size()); }
};

#endif
