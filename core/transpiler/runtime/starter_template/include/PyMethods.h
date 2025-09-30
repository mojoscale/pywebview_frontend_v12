
#include "PyInt.h"
#include "PyFloat.h"
#include "PyBool.h"
#include "PyList.h"
#include "PyString.h"

#include "PyInt.h"

#include "PyDict.h"
#include <Arduino.h>

#include <WString.h>


#include <type_traits>

// ========== py_int ==========


inline int py_int(int x) {
    return x;
}

inline int py_int(float x) {
    return static_cast<int>(x);
}

inline int py_int(double x) {
    return static_cast<int>(x);
}

inline int py_int(bool x) {
    return x ? 1L : 0L;
}

inline int py_int(const char* x) {
    return atol(x);
}

inline int py_int(const String& x) {
    return x.toInt();
}

// ========== py_float ==========

inline float py_float(int x) {
    return static_cast<float>(x);
}

inline float py_float(float x) {
    return x;
}

inline float py_float(double x) {
    return static_cast<float>(x);
}

inline float py_float(bool x) {
    return x ? 1.0f : 0.0f;
}

inline float py_float(const String& x) {
    return x.toFloat();
}

inline float py_float(const char* x) {
    return atof(x);
}

// ========== py_bool ==========

inline bool py_bool(int x) {
    return x != 0;
}

inline bool py_bool(float x) {
    return x != 0.0f;
}

inline bool py_bool(double x) {
    return x != 0.0;
}

inline bool py_bool(bool x) {
    return x;
}

inline bool py_bool(const String& x) {
    return x.length() > 0;
}

inline bool py_bool(const char* x) {
    return strlen(x) > 0;
}

// ========== py_str ==========

inline String py_str(int x) {
    return String(x);
}

inline String py_str(float x) {
    return String(x, 6);
}

inline String py_str(double x) {
    return String(x, 6);
}

inline String py_str(bool x) {
    return x ? "True" : "False";
}

inline String py_str(const String& x) {
    return x;
}

inline String py_str(const char* x) {
    return String(x);
}


//define the abs method same as in python

// ========== py_abs Overloads (Python-style absolute value) ==========
// ========== py_abs ==========

inline int py_abs(int x) {
    return (x < 0) ? -x : x;
}


inline float py_abs(float x) {
    return (x < 0.0f) ? -x : x;
}

inline double py_abs(double x) {
    return (x < 0.0) ? -x : x;
}

inline float py_abs(bool x) {
    return x ? 1.0f : 0.0f;
}

/*inline float py_abs(const String& s) {
    return py_abs(s.toFloat());
}*/



////////////////////////////////////////////////////////////////////////////////////////////////////


////////////////////////////////////////////////////////////////////////////////////////////////////

//define ascii method same as in python
// ========== py_ascii ==========

inline String py_ascii(const String& input) {
    String result = "'";
    for (size_t i = 0; i < input.length(); i++) {
        unsigned char c = input[i];
        if (c >= 32 && c <= 126) {
            result += (char)c;
        } else {
            char buf[5];
            sprintf(buf, "\\x%02X", c);
            result += buf;
        }
    }
    result += "'";
    return result;
}


////////////////////////////////////////////////////////////////////////////////////////////////////

///////////////////////////////////////////////////////////////////////////////////////////////////

// ========== py_bin ==========

inline String py_bin(int num) {
    bool is_negative = num < 0;
    unsigned int abs_val = is_negative ? -num : num;
    String result = "";

    if (abs_val == 0) {
        result = "0";
    } else {
        while (abs_val > 0) {
            result = (abs_val % 2 ? "1" : "0") + result;
            abs_val /= 2;
        }
    }

    if (is_negative) {
        result = "-0b" + result;
    } else {
        result = "0b" + result;
    }
    return result;
}

//////////////////////////////////////////////////////////////////////////////////////////////////////////


////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

// Python-style chr(): int → str
// ========== py_chr ==========

inline String py_chr(int codepoint) {
    if (codepoint < 0 || codepoint > 255) {
        return "?";  // fallback
    }
    char c[2];
    c[0] = static_cast<char>(codepoint);
    c[1] = '\0';
    return String(c);
}


////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////


/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////


PyList<int> py_divmod(int a, int b) {
    PyList<int> result;
    if (b == 0) {
        Serial.println("ZeroDivisionError: division or modulo by zero");
        result.append(0);
        result.append(0);
        return result;
    }
    result.append(a / b);
    result.append(a % b);
    return result;
}


/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////



//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////


// ========== py_hex ==========

inline String py_hex(int num) {
    bool is_negative = num < 0;
    unsigned int abs_val = is_negative ? -num : num;

    char buffer[12];
    snprintf(buffer, sizeof(buffer), "%s0x%lX", is_negative ? "-" : "", abs_val);

    String result = String(buffer);
    result.toLowerCase();
    return result;
}


/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////


////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

// ========== py_len ==========

inline int py_len(const String& s) {
    return s.length();
}

template<typename T>
inline int py_len(const PyList<T>& list) {
    return list.size();
}



/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////


///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// ========== py_list ==========

// From String → PyList<String> (character split)
inline PyList<String> py_list(const String& s) {
    PyList<String> result;
    for (int i = 0; i < s.length(); ++i) {
        result.append(String(s[i]));
    }
    return result;
}




////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////


/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////


// ========== py_oct ==========

inline String py_oct(int num) {
    bool is_negative = num < 0;
    unsigned int abs_val = is_negative ? -num : num;
    String result = "";

    do {
        result = String(abs_val % 8) + result;
        abs_val /= 8;
    } while (abs_val > 0);

    if (is_negative) {
        result = "-0o" + result;
    } else {
        result = "0o" + result;
    }
    return result;
}


////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////


// ========== py_ord ==========

inline int py_ord(const String& s) {
    if (s.length() != 1) {
        Serial.println("TypeError: ord() expected a character, but got a string of length != 1");
        return -1;
    }
    return (int)s[0];
}



////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////


////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// ========== py_pow ==========

inline int py_pow(int base, int exp) {
    if (exp < 0) {
        Serial.println("ValueError: Negative exponent not supported for integers");
        return -1;
    }

    int result = 1;
    for (int i = 0; i < exp; ++i) {
        result *= base;
    }
    return result;
}

inline int py_pow(int base, int exp, int mod) {
    if (exp < 0 || mod == 0) {
        Serial.println("ValueError: Negative exponent or zero modulus not supported");
        return -1;
    }

    int result = 1;
    base %= mod;
    while (exp > 0) {
        if (exp % 2 == 1)
            result = (result * base) % mod;
        base = (base * base) % mod;
        exp /= 2;
    }
    return result;
}

inline float py_pow(float base, float exp) {
    return powf(base, exp);
}


//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// ========== py_print ==========
void py_print() {
    Serial.println();
}

// Special handling for bool to print "True"/"False"
inline void py_print_single(const bool& value) {
    Serial.print(value ? F("True") : F("False"));
}

// Handle String objects directly
inline void py_print_single(const String& value) {
    Serial.print(value);
}

// Handle C-style strings
inline void py_print_single(const char* value) {
    Serial.print(value);
}

// Handle flash-stored strings (PROGMEM)
inline void py_print_single(const __FlashStringHelper* value) {
    Serial.print(value);
}

// Numeric types (int, float, etc.)
template<typename T>
typename std::enable_if<std::is_arithmetic<T>::value && !std::is_same<T, bool>::value>::type
py_print_single(const T& value) {
    Serial.print(value);
}

// Fallback for objects with to_string() method
template<typename T>
typename std::enable_if<!std::is_arithmetic<T>::value &&
                        !std::is_same<T, String>::value &&
                        !std::is_same<T, const char*>::value &&
                        !std::is_same<T, bool>::value &&
                        !std::is_same<T, const __FlashStringHelper*>::value>::type
py_print_single(const T& value) {
    Serial.print(value.to_string());
}

// Single argument version with newline
template<typename T>
void py_print(const T& value) {
    py_print_single(value);
    Serial.println();
}

// Multiple arguments version
template<typename T, typename... Args>
void py_print(const T& first, const Args&... rest) {
    py_print_single(first);
    Serial.print(F(" "));  // Space between items
    py_print(rest...);     // Recurse
}


///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////


///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

// ========== py_reversed ==========

// Reverse a PyList
template<typename T>
inline PyList<T> py_reversed(const PyList<T>& list) {
    PyList<T> result;
    for (int i = list.size() - 1; i >= 0; --i) {
        result.append(list[i]);
    }
    return result;
}

// Reverse a String
inline String py_reversed(const String& s) {
    String reversed = "";
    for (int i = s.length() - 1; i >= 0; --i) {
        reversed += s[i];
    }
    return reversed;
}


//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////


///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////


inline int py_round(float x) {
    return (x >= 0.0f) ? (int)(x + 0.5f) : (int)(x - 0.5f);
}

inline int py_round(double x) {
    return (x >= 0.0) ? (int)(x + 0.5) : (int)(x - 0.5);
}

//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////


/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

// ========== py_sorted ==========

// Sort a PyList (ascending)
template<typename T>
inline PyList<T> py_sorted(const PyList<T>& list) {
    PyList<T> result = list.copy();  // make a copy first
    result.sort();
    return result;
}

// Sort a String
inline String py_sorted(const String& s) {
    String sorted = s;
    int n = sorted.length();

    for (int i = 0; i < n; ++i) {
        for (int j = 0; j < n - i - 1; ++j) {
            if (sorted[j] > sorted[j + 1]) {
                char temp = sorted[j];
                sorted[j] = sorted[j + 1];
                sorted[j + 1] = temp;
            }
        }
    }

    return sorted;
}


/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

// ========== py_sum ==========

template<typename T>
inline T py_sum(const PyList<T>& list) {
    T total = T();  // default initialize
    for (int i = 0; i < list.size(); ++i) {
        total += list[i];
    }
    return total;
}

///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

//non python helper method to concat strings.

String concat_all(std::initializer_list<String> parts) {
    String out = "";
    for (const auto& s : parts) {
        out += String(s);  // ✅ double-wrapped: ensures conversion
    }
    return out;
}



///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////