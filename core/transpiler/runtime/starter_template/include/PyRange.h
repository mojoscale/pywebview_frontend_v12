#ifndef PYRANGE_H
#define PYRANGE_H

#include <Arduino.h>

class PyRange {
private:
    const int start_;
    const int stop_;
    const int step_;
    int current_;

public:
    // ========== CONSTRUCTORS ==========
    explicit PyRange(int stop)
        : start_(0), stop_(stop), step_(1), current_(start_) {}

    PyRange(int start, int stop)
        : start_(start), stop_(stop), step_(1), current_(start_) {}

    PyRange(int start, int stop, int step)
        : start_(start), stop_(stop), step_(step), current_(start_) {
        // Step validation - could add error handling if needed
    }

    // ========== COPY OPERATIONS (DELETED) ==========
    PyRange(const PyRange&) = delete;
    PyRange& operator=(const PyRange&) = delete;

    // ========== MOVE OPERATIONS ==========
    PyRange(PyRange&& other) noexcept
        : start_(other.start_), stop_(other.stop_),
          step_(other.step_), current_(other.current_) {}

    PyRange& operator=(PyRange&& other) noexcept {
        if (this != &other) {
            // const members can't be assigned, only current_ can be moved
            const_cast<int&>(start_) = other.start_;
            const_cast<int&>(stop_) = other.stop_;
            const_cast<int&>(step_) = other.step_;
            current_ = other.current_;
        }
        return *this;
    }

    // ========== ITERATOR METHODS ==========
    
    /**
     * @brief Reset the iterator to start position
     */
    void reset() {
        current_ = start_;
    }

    /**
     * @brief Check if there are more elements to iterate over
     * @return true if more elements available, false otherwise
     */
    bool has_next() const {
        if (step_ > 0)
            return current_ < stop_;
        else if (step_ < 0)
            return current_ > stop_;
        else
            return false; // step_ == 0 is invalid
    }

    /**
     * @brief Get the next element and advance the iterator
     * @return Current element value before advancing
     */
    int next() {
        if (!has_next()) {
            // Option 1: Return last valid value
            // Option 2: Reset and return start
            // Option 3: Return error value
            // For now, return current without advancing
            return current_;
        }
        int value = current_;
        current_ += step_;
        return value;
    }

    // ========== RANGE PROPERTIES ==========
    
    /**
     * @brief Calculate the number of elements in the range
     * @return Size of the range (number of elements)
     */
    int size() const {
        if (step_ == 0) return 0;
        
        int distance = stop_ - start_;
        
        // Check if range is empty
        if ((step_ > 0 && distance <= 0) || (step_ < 0 && distance >= 0)) {
            return 0;
        }
        
        // Calculate number of steps
        int steps = distance / step_;
        if (distance % step_ != 0) 
            steps += 1;
            
        return steps > 0 ? steps : 0;
    }

    /**
     * @brief Check if range contains no elements
     * @return true if range is empty, false otherwise
     */
    bool is_empty() const {
        return size() == 0;
    }

    /**
     * @brief Boolean conversion for truthiness checking
     * @return true if range is non-empty, false if empty
     */
    explicit operator bool() const {
        return !is_empty();
    }

    // ========== ELEMENT ACCESS ==========
    
    /**
     * @brief Access element by index (Python-style indexing)
     * @param index Zero-based index
     * @return Element value at specified index
     */
    int operator[](int index) const {
        if (index < 0 || index >= size()) {
            // Index out of bounds - return start or handle error
            return start_;
        }
        return start_ + index * step_;
    }

    /**
     * @brief Get element by index with bounds checking
     * @param index Zero-based index
     * @param default_val Value to return if index out of bounds
     * @return Element value or default_val if index invalid
     */
    int get(int index, int default_val = 0) const {
        if (index < 0 || index >= size()) {
            return default_val;
        }
        return start_ + index * step_;
    }

    // ========== RANGE CHECKS ==========
    
    /**
     * @brief Check if value is contained in the range
     * @param value Value to check
     * @return true if value is in range, false otherwise
     */
    bool contains(int value) const {
        if (step_ > 0) {
            return value >= start_ && value < stop_ && (value - start_) % step_ == 0;
        } else if (step_ < 0) {
            return value <= start_ && value > stop_ && (start_ - value) % (-step_) == 0;
        }
        return false;
    }

    // ========== GETTERS ==========
    int start() const { return start_; }
    int stop() const { return stop_; }
    int step() const { return step_; }
    int current() const { return current_; }

    // ========== STRING REPRESENTATION ==========
    
    /**
     * @brief Convert range to string representation
     * @return String representation of the range
     */
    String to_string() const {
        char buffer[32]; // Fixed buffer to avoid dynamic allocation
        if (step_ == 1) {
            snprintf(buffer, sizeof(buffer), "range(%d, %d)", start_, stop_);
        } else {
            snprintf(buffer, sizeof(buffer), "range(%d, %d, %d)", start_, stop_, step_);
        }
        return String(buffer);
    }

    /**
     * @brief Print range to Serial
     */
    void print() const {
        Serial.println(to_string());
    }

    // ========== RANGE SLICING ==========
    
    /**
     * @brief Create a subrange (Python-style slicing)
     * @param start Start index (inclusive)
     * @param stop Stop index (exclusive)
     * @param step Step size
     * @return New PyRange object
     */
    PyRange slice(int start, int stop, int step = 1) const {
        int new_start = (*this)[start];
        int new_stop = (*this)[stop];
        return PyRange(new_start, new_stop, step * step_);
    }

    /**
     * @brief Create a subrange from start to end
     * @param start Start index (inclusive)
     * @return New PyRange from start to original stop
     */
    PyRange from_index(int start) const {
        return slice(start, size());
    }

    /**
     * @brief Create a subrange from start to stop
     * @param start Start index (inclusive)
     * @param stop Stop index (exclusive)
     * @return New PyRange object
     */
    PyRange subrange(int start, int stop) const {
        return slice(start, stop);
    }

    // ========== DESTRUCTOR ==========
    ~PyRange() = default;
};

// ========== HELPER FUNCTIONS ==========

/**
 * @brief Create a range from 0 to stop (exclusive)
 * @param stop End value (exclusive)
 * @return PyRange object
 */
inline PyRange py_range(int stop) {
    return PyRange(stop);
}

/**
 * @brief Create a range from start to stop (exclusive)
 * @param start Start value (inclusive)
 * @param stop End value (exclusive)
 * @return PyRange object
 */
inline PyRange py_range(int start, int stop) {
    return PyRange(start, stop);
}

/**
 * @brief Create a range from start to stop with step
 * @param start Start value (inclusive)
 * @param stop End value (exclusive)
 * @param step Step size
 * @return PyRange object
 */
inline PyRange py_range(int start, int stop, int step) {
    return PyRange(start, stop, step);
}

/**
 * @brief Create a range from 0 to stop with step 1 (alias for py_range(stop))
 * @param stop End value (exclusive)
 * @return PyRange object
 */
inline PyRange range(int stop) {
    return PyRange(stop);
}

/**
 * @brief Create a range from start to stop with step 1 (alias for py_range(start, stop))
 * @param start Start value (inclusive)
 * @param stop End value (exclusive)
 * @return PyRange object
 */
inline PyRange range(int start, int stop) {
    return PyRange(start, stop);
}

/**
 * @brief Create a range from start to stop with custom step (alias for py_range(start, stop, step))
 * @param start Start value (inclusive)
 * @param stop End value (exclusive)
 * @param step Step size
 * @return PyRange object
 */
inline PyRange range(int start, int stop, int step) {
    return PyRange(start, stop, step);
}

#endif // PYRANGE_H