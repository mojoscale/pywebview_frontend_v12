#ifndef STEPPER_WRAPPER_H
#define STEPPER_WRAPPER_H

#include <Arduino.h>
#include "PyDict.h"
#include <FastAccelStepper.h>

// Wrapper methods for FastAccelStepper that return PyDict with MoveResultCode
// These wrappers convert MoveResultCode enum to PyDict<int> for easy serialization

PyDict<int> custom_stepper_move(FastAccelStepper* stepper, int32_t steps, bool blocking = false) {
    PyDict<int> result;
    MoveResultCode code = stepper->move(steps, blocking);
    
    result.set("result_code", (int)code);
    result.set("steps", steps);
    result.set("blocking", blocking ? 1 : 0);
    result.set("success", (int)code == 0 ? 1 : 0);
    
    return result;
}

PyDict<int> custom_stepper_move_to(FastAccelStepper* stepper, int32_t position, bool blocking = false) {
    PyDict<int> result;
    MoveResultCode code = stepper->moveTo(position, blocking);
    
    result.set("result_code", (int)code);
    result.set("position", position);
    result.set("blocking", blocking ? 1 : 0);
    result.set("success", (int)code == 0 ? 1 : 0);
    
    return result;
}

PyDict<int> custom_stepper_run_forward(FastAccelStepper* stepper) {
    PyDict<int> result;
    MoveResultCode code = stepper->runForward();
    
    result.set("result_code", (int)code);
    result.set("operation", 1); // 1 = forward
    result.set("success", (int)code == 0 ? 1 : 0);
    
    return result;
}

PyDict<int> custom_stepper_run_backward(FastAccelStepper* stepper) {
    PyDict<int> result;
    MoveResultCode code = stepper->runBackward();
    
    result.set("result_code", (int)code);
    result.set("operation", -1); // -1 = backward
    result.set("success", (int)code == 0 ? 1 : 0);
    
    return result;
}

PyDict<int> custom_stepper_move_by_acceleration(FastAccelStepper* stepper, int32_t acceleration, 
                                       bool blocking = false) {
    PyDict<int> result;
    MoveResultCode code = stepper->moveByAcceleration(acceleration, blocking);
    
    result.set("result_code", (int)code);
    result.set("acceleration", acceleration);
    result.set("blocking", blocking ? 1 : 0);
    result.set("success", (int)code == 0 ? 1 : 0);
    
    return result;
}

// Utility function to get human-readable description of MoveResultCode
// Result code 0 = success, all other codes are error states
String custom_get_move_result_description(int result_code) {
    if (result_code == 0) {
        return "SUCCESS: Command accepted and queued";
    }
    
    // For error codes, return a generic message with the code
    // The actual error codes depend on FastAccelStepper version
    return "ERROR: Result code " + String(result_code);
}

#endif