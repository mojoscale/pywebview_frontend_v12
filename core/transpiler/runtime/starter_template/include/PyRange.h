#ifndef PYRANGE_H
#define PYRANGE_H

#include <Arduino.h>

class PyRange {
private:
    int start_;
    int stop_;
    int step_;
    int current_;

public:
    // Constructors
    PyRange(int stop)
        : start_(0), stop_(stop), step_(1), current_(0) {}

    PyRange(int start, int stop)
        : start_(start), stop_(stop), step_(1), current_(start) {}

    PyRange(int start, int stop, int step)
        : start_(start), stop_(stop), step_(step), current_(start) {}

    // ✅ Copy constructor
    PyRange(const PyRange& other)
        : start_(other.start_), stop_(other.stop_),
          step_(other.step_), current_(other.current_) {}

    // ✅ Copy assignment
    PyRange& operator=(const PyRange& other) {
        if (this != &other) {
            start_ = other.start_;
            stop_ = other.stop_;
            step_ = other.step_;
            current_ = other.current_;
        }
        return *this;
    }

    // ✅ Move constructor
    PyRange(PyRange&& other) noexcept
        : start_(other.start_), stop_(other.stop_),
          step_(other.step_), current_(other.current_) {}

    // ✅ Move assignment
    PyRange& operator=(PyRange&& other) noexcept {
        if (this != &other) {
            start_ = other.start_;
            stop_ = other.stop_;
            step_ = other.step_;
            current_ = other.current_;
        }
        return *this;
    }

    // Reset iterator
    void reset() {
        current_ = start_;
    }

    // Check if there are more elements
    bool has_next() const {
        if (step_ > 0)
            return current_ < stop_;
        else
            return current_ > stop_;
    }

    // Get next element and advance
    int next() {
        int value = current_;
        current_ += step_;
        return value;
    }

    // Size of the range
    int size() const {
        if (step_ == 0) return 0; // Prevent division by zero
        int distance = stop_ - start_;
        int steps = distance / step_;
        if (distance % step_ != 0) steps += 1;
        return steps > 0 ? steps : 0;
    }

    // Indexing: get item at index
    int operator[](int index) const {
        int value = start_ + index * step_;
        if ((step_ > 0 && value >= stop_) ||
            (step_ < 0 && value <= stop_)) {
            return 0; // Or Serial.println error
        }
        return value;
    }

    // Getters
    int start() const { return start_; }
    int stop() const { return stop_; }
    int step() const { return step_; }

    // String representation
    String to_string() const {
        return "Range(" + String(start_) + ", " + String(stop_) + ", " + String(step_) + ")";
    }
};

// ========== py_range() helper functions ==========

inline PyRange py_range(int stop) {
    return PyRange(stop);
}

inline PyRange py_range(int start, int stop) {
    return PyRange(start, stop);
}

inline PyRange py_range(int start, int stop, int step) {
    return PyRange(start, stop, step);
}

#endif
