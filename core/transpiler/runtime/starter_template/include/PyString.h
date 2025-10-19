#ifndef PYSTRING_H
#define PYSTRING_H

#include <Arduino.h>
#include <vector>
#include <ctype.h>
#include "PyInt.h"
#include "PyList.h"

class PyString {
private:
    String data;

public:
    PyString() : data("") {}
    PyString(const char* s) : data(s) {}
    PyString(char c) : data(String(c)) {}  // ✅ Handle single char
    PyString(const String& s) : data(s) {}

    // ✅ Copy constructor - handles const PyString&
    PyString(const PyString& other) : data(other.data) {}

    // ✅ Non-const copy constructor - handles PyString&
    PyString(PyString& other) : data(other.data) {}

    // ✅ Copy assignment - handles const PyString&
    PyString& operator=(const PyString& other) {
        if (this != &other) {
            data = other.data;
        }
        return *this;
    }

    // ✅ Non-const copy assignment - handles PyString&
    PyString& operator=(PyString& other) {
        if (this != &other) {
            data = other.data;
        }
        return *this;
    }

    // ✅ Move constructor
    PyString(PyString&& other) noexcept : data(std::move(other.data)) {}

    // ✅ Move assignment
    PyString& operator=(PyString&& other) noexcept {
        if (this != &other) {
            data = std::move(other.data);
        }
        return *this;
    }

    void print() const {
        Serial.println(data);
    }

    String str() const {
        return data;
    }

    int len() const {
        return data.length();
    }

    bool contains(const String& substring) const {
        return data.indexOf(substring) != -1;
    }

    String operator[](int index) const {
        if (index < 0 || index >= (int)data.length()) return "";
        return String(data.charAt(index));
    }

    String lower() const {
        String result = data;
        result.toLowerCase();
        return result;
    }

    String upper() const {
        String result = data;
        result.toUpperCase();
        return result;
    }

    String strip() const {
        String result = data;
        result.trim();
        return result;
    }

    String capitalize() const {
        if (data.length() == 0) return "";
        String result = data;
        result[0] = toupper(result[0]);
        for (size_t i = 1; i < result.length(); ++i) {
            result[i] = tolower(result[i]);
        }
        return result;
    }

    String title() const {
        String result = data;
        bool newWord = true;
        for (size_t i = 0; i < result.length(); ++i) {
            if (::isspace(result[i])) {
                newWord = true;
            } else {
                result[i] = newWord ? toupper(result[i]) : tolower(result[i]);
                newWord = false;
            }
        }
        return result;
    }

    String replace(const String& from, const String& to) const {
        String result = data;
        result.replace(from, to);
        return result;
    }

    String replace(const PyString& from, const PyString& to) const {
        return replace(from.str(), to.str());
    }

    String lstrip() const {
        int start = 0;
        while (start < (int)data.length() && ::isspace(data[start])) start++;
        return data.substring(start);
    }

    String rstrip() const {
        int end = data.length() - 1;
        while (end >= 0 && ::isspace(data[end])) end--;
        return data.substring(0, end + 1);
    }

    String zfill(int width) const {
        int pad = width - data.length();
        if (pad > 0) {
            String padding = "";
            for (int i = 0; i < pad; ++i) padding += "0";
            return padding + data;
        }
        return data;
    }

    int rindex(const String& sub) const {
        int idx = data.lastIndexOf(sub);
        if (idx == -1) {
            Serial.println("ValueError: substring not found in rindex()");
        }
        return idx;
    }

    void append(const String& s) {
        data += s;
    }

    int index(const String& sub) const {
        int idx = data.indexOf(sub);
        if (idx == -1) {
            Serial.println("ValueError: substring not found");
            return -1;
        }
        return idx;
    }

    int index(const PyString& sub) const {
        return index(sub.str());
    }

    int find(const String& sub) const {
        return data.indexOf(sub);
    }

    int find(const PyString& sub) const {
        return data.indexOf(sub.str());
    }

    int rfind(const String& sub) const {
        return data.lastIndexOf(sub);
    }

    int rfind(const PyString& sub) const {
        return data.lastIndexOf(sub.str());
    }

    bool startswith(const String& prefix) const {
        return data.startsWith(prefix);
    }

    bool startswith(const PyString& prefix) const {
        return data.startsWith(prefix.str());
    }

    bool endswith(const String& suffix) const {
        return data.endsWith(suffix);
    }

    bool endswith(const PyString& suffix) const {
        return data.endsWith(suffix.str());
    }

    int count(const String& sub) const {
        int count = 0, idx = 0;
        while ((idx = data.indexOf(sub, idx)) != -1) {
            count++;
            idx += sub.length();
        }
        return count;
    }

    int count(const PyString& sub) const {
        return count(sub.str());
    }

    bool islower() const {
        for (size_t i = 0; i < data.length(); ++i)
            if (isAlpha(data[i]) && !::islower(data[i])) return false;
        return true;
    }

    bool isupper() const {
        for (size_t i = 0; i < data.length(); ++i)
            if (isAlpha(data[i]) && !::isupper(data[i])) return false;
        return true;
    }

    bool isnumeric() const {
        if (data.length() == 0) return false;
        for (size_t i = 0; i < data.length(); ++i)
            if (data[i] < '0' || data[i] > '9') return false;
        return true;
    }

    bool isdigit() const {
        for (size_t i = 0; i < data.length(); ++i)
            if (!isDigit(data[i])) return false;
        return true;
    }

    bool isalpha() const {
        for (size_t i = 0; i < data.length(); ++i)
            if (!isAlpha(data[i])) return false;
        return true;
    }

    bool isdecimal() const {
        return isnumeric();
    }

    bool isalnum() const {
        for (size_t i = 0; i < data.length(); ++i)
            if (!isAlphaNumeric(data[i])) return false;
        return true;
    }

    bool pyisspace() const {
        for (size_t i = 0; i < data.length(); ++i)
            if (!::isspace(data[i])) return false;
        return true;
    }

    bool istitle() const {
        bool newWord = true, foundAlpha = false;
        for (size_t i = 0; i < data.length(); ++i) {
            char c = data[i];
            if (::isspace(c)) newWord = true;
            else if (::isalpha(c)) {
                if (newWord && !::isupper(c)) return false;
                if (!newWord && !::islower(c)) return false;
                newWord = false;
                foundAlpha = true;
            } else newWord = false;
        }
        return foundAlpha;
    }

    String removeprefix(const String& prefix) const {
        if (data.startsWith(prefix)) return data.substring(prefix.length());
        return data;
    }

    String removesuffix(const String& suffix) const {
        if (data.endsWith(suffix)) return data.substring(0, data.length() - suffix.length());
        return data;
    }

    String ljust(int width, char fillchar = ' ') const {
        int pad = width - data.length();
        if (pad <= 0) return data;
        String result = data;
        for (int i = 0; i < pad; ++i) result += fillchar;
        return result;
    }

    String ljust(int width, const String& fillchar) const {
        return ljust(width, fillchar.length() > 0 ? fillchar[0] : ' ');
    }

    String rjust(int width, char fillchar = ' ') const {
        int pad = width - data.length();
        if (pad <= 0) return data;
        String result = "";
        for (int i = 0; i < pad; ++i) result += fillchar;
        result += data;
        return result;
    }

    String rjust(int width, const String& fillchar) const {
        return rjust(width, fillchar.length() > 0 ? fillchar[0] : ' ');
    }

    String slice(int start, int end) const {
        int len = data.length();
        if (start < 0) start += len;
        if (end < 0) end += len;

        start = constrain(start, 0, len);
        end = constrain(end, 0, len);

        if (start >= end) return "";
        return data.substring(start, end);
    }

    String swapcase() const {
        String result = "";
        for (size_t i = 0; i < data.length(); ++i) {
            char c = data[i];
            if (::isupper(c)) result += (char)::tolower(c);
            else if (::islower(c)) result += (char)::toupper(c);
            else result += c;
        }
        return result;
    }

    PyList<String> split() const {
        PyList<String> parts;
        size_t start = 0, i = 0;
        while (i < data.length()) {
            while (i < data.length() && ::isspace(data[i])) ++i;
            start = i;
            while (i < data.length() && !::isspace(data[i])) ++i;
            if (start < i) parts.append(data.substring(start, i));
        }
        return parts;
    }

    PyList<String> split(const String& delimiter) const {
        PyList<String> parts;
        if (delimiter.length() == 0) {
            for (int i = 0; i < data.length(); ++i) {
                parts.append(String(data[i]));
            }
            return parts;
        }

        int start = 0, end = data.indexOf(delimiter);
        while (end != -1) {
            parts.append(data.substring(start, end));
            start = end + delimiter.length();
            end = data.indexOf(delimiter, start);
        }
        parts.append(data.substring(start));
        return parts;
    }

    PyList<String> split(const char* delimiter) const {
        return split(String(delimiter));
    }

    PyList<String> rsplit(const String& delimiter) const {
        PyList<String> parts;
        if (delimiter.length() == 0) {
            parts.append(data);
            return parts;
        }
        int end = data.length(), idx = data.lastIndexOf(delimiter);
        while (idx != -1) {
            parts.insert(0, data.substring(idx + delimiter.length(), end));
            end = idx;
            idx = data.lastIndexOf(delimiter, idx - 1);
        }
        parts.insert(0, data.substring(0, end));
        return parts;
    }

    // ✅ Original join - for PyList<String>
    String join(const PyList<String>& parts) const {
        String result = "";
        for (int i = 0; i < parts.size(); ++i) {
            result += parts[i];
            if (i < parts.size() - 1) result += data;
        }
        return result;
    }

    // ✅ Extended join - for PyList<int>
    String join(const PyList<int>& parts) const {
        String result = "";
        for (int i = 0; i < parts.size(); ++i) {
            result += String(parts[i]);
            if (i < parts.size() - 1) result += data;
        }
        return result;
    }

    // ✅ Extended join - for PyList<float>
    String join(const PyList<float>& parts) const {
        String result = "";
        for (int i = 0; i < parts.size(); ++i) {
            result += String(parts[i]);
            if (i < parts.size() - 1) result += data;
        }
        return result;
    }

    // ✅ Extended join - for PyList<bool>
    String join(const PyList<bool>& parts) const {
        String result = "";
        for (int i = 0; i < parts.size(); ++i) {
            result += (parts[i] ? "True" : "False");
            if (i < parts.size() - 1) result += data;
        }
        return result;
    }

    // ✅ Universal join template - for any PyList type
    template<typename T>
    String join(const PyList<T>& parts) const {
        String result = "";
        for (int i = 0; i < parts.size(); ++i) {
            // Handles custom types with str() method
            result += parts[i].str();
            if (i < parts.size() - 1) result += data;
        }
        return result;
    }

    String encode() const {
        return data;
    }

    static PyString decode(const String& bytes) {
        return PyString(bytes);
    }

    static PyString decode(const PyString& bytes) {
        return PyString(bytes.str());
    }

    PyString& operator+=(const String& rhs) {
        data += rhs;
        return *this;
    }

    PyString& operator+=(const PyString& rhs) {
        data += rhs.str();
        return *this;
    }

    bool operator==(const String& other) const {
        return data == other;
    }

    bool operator==(const PyString& other) const {
        return data == other.data;
    }

    bool operator!=(const PyString& other) const {
        return !(*this == other);
    }
};

#endif