# Arduino.h Python Function Equivalents with Type Annotations

# ---- Macros as Constants ----
HIGH: int = 1
LOW: int = 0

INPUT: int = 0x0
OUTPUT: int = 0x1
INPUT_PULLUP: int = 0x2

CHANGE: int = 1
FALLING: int = 2
RISING: int = 3

LSBFIRST: int = 0
MSBFIRST: int = 1


__include_modules__ = ""
__dependencies__ = ""

# ---- Functions ----


def pinMode(pin: int, mode: int) -> None:
    """
    Configures the specified pin to behave either as an input or an output.

    Args:
        pin (int): The number of the pin whose mode you want to set.
        mode (int): The mode to set for the pin. Common values are:
            - INPUT (0x0): Configures the pin as an input.
            - OUTPUT (0x1): Configures the pin as an output.
            - INPUT_PULLUP (0x2): Configures the pin as an input with an internal pull-up resistor.

    Returns:
        None
    """
    __use_as_is__: bool = True
    raise NotImplementedError("pinMode is not implemented")


def digitalWrite(pin: int, val: int) -> None:
    """
    Write a HIGH or LOW value to a digital pin.

    Args:
        pin (int): The number of the digital pin to write to.
        val (int): The value to write. Use HIGH (1) or LOW (0).

    Returns:
        None
    """
    __use_as_is__: bool = True
    raise NotImplementedError("digitalWrite is not implemented")


def digitalRead(pin: int) -> int:
    """
    Reads the value from a specified digital pin, either HIGH or LOW.

    Args:
        pin (int): The number of the digital pin to read from.

    Returns:
        int: The value read from the pin — HIGH (1) or LOW (0).
    """
    __use_as_is__: bool = True
    raise NotImplementedError("digitalRead is not implemented")


def analogRead(pin: int) -> int:
    """
    Reads the value from the specified analog pin.

    Args:
        pin (int): The number of the analog pin to read from.

    Returns:
        int: The analog value read from the pin, typically ranging from 0 to 1023 (10-bit ADC),
             or up to 4095 (12-bit) on some boards like ESP32.
    """
    __use_as_is__: bool = True
    raise NotImplementedError("analogRead is not implemented")


def analogWrite(pin: int, val: int) -> None:
    """
    Writes an analog value (PWM wave) to a pin.

    Args:
        pin (int): The number of the digital pin to write to (supports PWM).
        val (int): The duty cycle: a value between 0 (always off) and 255 (always on) for 8-bit resolution.

    Returns:
        None
    """
    __use_as_is__: bool = True
    raise NotImplementedError("analogWrite is not implemented")


def delay(ms: int) -> None:
    """
    Pauses the program for the amount of time (in milliseconds) specified.

    Args:
        ms (int): The number of milliseconds to pause.

    Returns:
        None
    """
    __use_as_is__: bool = True
    raise NotImplementedError("delay is not implemented")


def delayMicroseconds(us: int) -> None:
    """
    Pauses the program for the specified time in microseconds.

    Args:
        us (int): The number of microseconds to pause.

    Returns:
        None
    """
    __use_as_is__: bool = True
    raise NotImplementedError("delayMicroseconds is not implemented")


def millis() -> int:
    """
    Returns the number of milliseconds since the program started running.

    Returns:
        int: Elapsed time in milliseconds.
    """
    raise NotImplementedError("millis is not implemented")


def micros() -> int:
    """
    Returns the number of microseconds since the program started running.

    Returns:
        int: Elapsed time in microseconds.
    """
    __use_as_is__: bool = True
    raise NotImplementedError("micros is not implemented")


def shiftOut(dataPin: int, clockPin: int, bitOrder: int, val: int) -> None:
    """
    Shifts out a byte of data one bit at a time.

    Args:
        dataPin (int): The pin on which to output each bit.
        clockPin (int): The pin to toggle to signal each bit.
        bitOrder (int): The order to shift bits out (e.g., MSBFIRST or LSBFIRST).
        val (int): The byte of data to shift out.

    Returns:
        None
    """
    __use_as_is__: bool = True
    raise NotImplementedError("shiftOut is not implemented")


def shiftIn(dataPin: int, clockPin: int, bitOrder: int) -> int:
    """
    Shifts in a byte of data one bit at a time.

    Args:
        dataPin (int): The pin from which to read each bit.
        clockPin (int): The pin to toggle to signal each bit.
        bitOrder (int): The order to shift bits in (e.g., MSBFIRST or LSBFIRST).

    Returns:
        int: The byte of data read.
    """
    __use_as_is__: bool = True
    raise NotImplementedError("shiftIn is not implemented")


def pulseIn(pin: int, state: int, timeout: int = 1000000) -> int:
    """
    Reads a pulse (either HIGH or LOW) on a pin.

    Args:
        pin (int): The pin to read the pulse from.
        state (int): The type of pulse to read: HIGH or LOW.
        timeout (int, optional): Timeout in microseconds (default is 1 second).

    Returns:
        int: The length of the pulse in microseconds (or 0 if timeout).
    """
    __use_as_is__: bool = True
    raise NotImplementedError("pulseIn is not implemented")


def tone(pin: int, frequency: int, duration: int = 0) -> None:
    """
    Generates a square wave of the specified frequency on a pin.

    Args:
        pin (int): The pin on which to generate the tone.
        frequency (int): The frequency of the tone in Hz.
        duration (int, optional): Duration of the tone in milliseconds (0 for continuous).

    Returns:
        None
    """
    __use_as_is__: bool = True
    raise NotImplementedError("tone is not implemented")


def noTone(pin: int) -> None:
    """
    Stops the generation of a tone on a pin.

    Args:
        pin (int): The pin to stop the tone on.

    Returns:
        None
    """
    __use_as_is__: bool = True
    raise NotImplementedError("noTone is not implemented")


def noInterrupts() -> None:
    """
    Disables all interrupts on the microcontroller.

    This function is typically used to ensure atomic access to shared resources
    or to prevent interruptions during critical timing-sensitive operations.

    Returns:
        None
    """
    __use_as_is__: bool = True
    raise NotImplementedError("noInterrupts is not implemented")


def interrupts() -> None:
    """
    Re-enables interrupts on the microcontroller.

    This should be called after `noInterrupts()` to restore normal interrupt behavior.

    Returns:
        None
    """
    __use_as_is__: bool = True
    raise NotImplementedError("interrupts is not implemented")


from typing import Callable


def attachInterrupt(pin: int, ISR: Callable[[], None], mode: int) -> None:
    """
    Attaches an interrupt to a pin, triggered on a particular mode.

    Args:
        pin (int): The pin to attach the interrupt to.
        ISR (Callable): A function to call when the interrupt is triggered.
        mode (int): The condition to trigger the interrupt (RISING, FALLING, or CHANGE).

    Returns:
        None
    """
    __use_as_is__: bool = True
    raise NotImplementedError("attachInterrupt is not implemented")


def detachInterrupt(pin: int) -> None:
    """
    Disables the interrupt for a given pin.

    Args:
        pin (int): The pin to detach the interrupt from.

    Returns:
        None
    """
    __use_as_is__: bool = True
    raise NotImplementedError("detachInterrupt is not implemented")


####################################################################  Math  ############################################################################################

# ---- Constants ----
PI: float = 3.141592653589793
HALF_PI: float = 1.5707963267948966
TWO_PI: float = 6.283185307179586
DEG_TO_RAD: float = 0.017453292519943295
RAD_TO_DEG: float = 57.29577951308232
EULER: float = 2.718281828459045

__include_modules__ = "math"
__dependencies__ = ""

# ---- Function Stubs ----


def math_min(a: float, b: float) -> float:
    """
    Returns the smaller of two values.

    Args:
        a (Any): First value.
        b (Any): Second value.

    Returns:
        Any: Smaller of the two values.

    """
    __use_as_is__ = False
    __translation__ = "min({0}, {1})"
    raise NotImplementedError()


def math_max(a: float, b: float) -> float:
    """
    Returns the larger of two values.

    Args:
        a (Any): First value.
        b (Any): Second value.

    Returns:
        Any: Larger of the two values.
    """
    __use_as_is__ = False
    __translation__ = "max({0}, {1})"
    raise NotImplementedError()


def math_abs(x: float) -> float:
    """
    Returns the absolute value.

    Args:
        x (float): Input value.

    Returns:
        float: Absolute value of x.

    """
    __use_as_is__ = False
    __translation__ = "abs({0})"
    raise NotImplementedError()


def math_constrain(x: float, a: float, b: float) -> float:
    """
    Constrains a number to be within a range.

    Args:
        x (float): Value to constrain.
        a (float): Minimum limit.
        b (float): Maximum limit.

    Returns:
        float: Constrained value.

    """
    __use_as_is__ = False
    __translation__ = "constrain({0}, {1}, {2})"
    raise NotImplementedError()


def math_map(
    x: float, in_min: float, in_max: float, out_min: float, out_max: float
) -> float:
    """
    Re-maps a number from one range to another.

    Args:
        x (float): Value to map.
        in_min (float): Input range min.
        in_max (float): Input range max.
        out_min (float): Output range min.
        out_max (float): Output range max.

    Returns:
        float: Mapped output.

    """
    __use_as_is__ = False
    __translation__ = "map({0}, {1}, {2}, {3}, {4})"
    raise NotImplementedError()


def math_pow(base: float, exponent: float) -> float:
    """
    Returns base raised to the power of exponent.

    Args:
        base (float): The base value.
        exponent (float): The exponent.

    Returns:
        float: base ** exponent.
    """
    __use_as_is__ = False
    __translation__ = "pow({0}, {1})"
    raise NotImplementedError()


def math_sqrt(x: float) -> float:
    """
    Returns the square root of x.

    Args:
        x (float): Input value.

    Returns:
        float: Square root of x.

    """
    __use_as_is__ = False
    __translation__ = "sqrt({0})"
    raise NotImplementedError()


def math_sq(x: float) -> float:
    """
    Returns the square of x.

    Args:
        x (float): Input value.

    Returns:
        float: x * x

    """
    __use_as_is__ = False
    __translation__ = "sq({0})"
    raise NotImplementedError()


def math_sin(radians: float) -> float:
    """
    Computes sine of an angle in radians.

    Args:
        radians (float): Angle in radians.

    Returns:
        float: sin(radians)

    """
    __use_as_is__ = False
    __translation__ = "sin({0})"
    raise NotImplementedError()


def math_cos(radians: float) -> float:
    """
    Computes cosine of an angle in radians.

    Args:
        radians (float): Angle in radians.

    Returns:
        float: cos(radians)

    """
    __use_as_is__ = False
    __translation__ = "cos({0})"
    raise NotImplementedError()


def math_tan(radians: float) -> float:
    """
    Computes tangent of an angle in radians.

    Args:
        radians (float): Angle in radians.

    Returns:
        float: tan(radians)

    """
    __use_as_is__ = False
    __translation__ = "tan({0})"
    raise NotImplementedError()


def math_radians(degrees: float) -> float:
    """
    Converts degrees to radians.

    Args:
        degrees (float): Angle in degrees.

    Returns:
        float: Angle in radians.

    """
    __use_as_is__ = False
    __translation__ = "radians({0})"
    raise NotImplementedError()


def math_degrees(radians: float) -> float:
    """
    Converts radians to degrees.

    Args:
        radians (float): Angle in radians.

    Returns:
        float: Angle in degrees.

    """
    __use_as_is__ = False
    __translation__ = "degrees({0})"
    raise NotImplementedError()


def math_round(x: float) -> int:
    """
    Rounds to the nearest integer.

    Args:
        x (float): Input value.

    Returns:
        int: Rounded value.

    """
    __use_as_is__ = False
    __translation__ = "round({0})"
    raise NotImplementedError()


def math_ceil(x: float) -> int:
    """
    Returns the smallest integer not less than x.

    Args:
        x (float): Input value.

    Returns:
        int: Ceil value.

    """
    __use_as_is__ = False
    __translation__ = "ceil({0})"
    raise NotImplementedError()


def math_floor(x: float) -> int:
    """
    Returns the largest integer not greater than x.

    Args:
        x (float): Input value.

    Returns:
        int: Floor value.

    """
    __use_as_is__ = False
    __translation__ = "floor({0})"
    raise NotImplementedError()


def math_fmod(x: float, y: float) -> float:
    """
    Returns the floating-point remainder of x / y.

    Args:
        x (float): Dividend.
        y (float): Divisor.

    Returns:
        float: Remainder.

    """
    __use_as_is__ = False
    __translation__ = "fmod({0}, {1})"
    raise NotImplementedError()


def math_log(x: float) -> float:
    """
    Returns natural logarithm (base e).

    Args:
        x (float): Input value.

    Returns:
        float: ln(x)

    """
    __use_as_is__ = False
    __translation__ = "log({0})"
    raise NotImplementedError()


def math_log10(x: float) -> float:
    """
    Returns base-10 logarithm.

    Args:
        x (float): Input value.

    Returns:
        float: log₁₀(x)

    """
    __use_as_is__ = False
    __translation__ = "log10({0})"
    raise NotImplementedError()


def math_exp(x: float) -> float:
    """
    Returns e raised to the power of x.

    Args:
        x (float): Input value.

    Returns:
        float: e^x

    """
    __use_as_is__ = False
    __translation__ = "exp({0})"
    raise NotImplementedError()


############################################Serial###########################################################3


def serial_begin(baudrate: int) -> None:
    """
    Sets the data rate in bits per second (baud) for serial data transmission.

    Args:
        baudrate (int): The baud rate (e.g., 9600, 115200)

    Returns:
        None
    """
    __use_as_is__ = False
    __translation__ = "Serial.begin({0})"
    raise NotImplementedError()


def serial_end() -> None:
    """
    Disables serial communication and releases the TX/RX pins.

    Returns:
        None
    """
    __use_as_is__ = False
    __translation__ = "Serial.end()"
    raise NotImplementedError()


def serial_available() -> int:
    """
    Returns the number of bytes available for reading from the serial buffer.

    Returns:
        int: Number of bytes available to read.
    """
    __use_as_is__ = False
    __translation__ = "Serial.available()"
    raise NotImplementedError()


def serial_read() -> int:
    """
    Reads incoming serial data.

    Returns:
        int: The first byte of incoming serial data, or -1 if no data is available.
    """
    __use_as_is__ = False
    __translation__ = "Serial.read()"
    raise NotImplementedError()


def serial_peek() -> int:
    """
    Returns the next byte of incoming serial data without removing it from the internal buffer.

    Returns:
        int: Next byte of incoming serial data, or -1 if no data is available.
    """
    __use_as_is__ = False
    __translation__ = "Serial.peek()"
    raise NotImplementedError()


def serial_flush() -> None:
    """
    Waits for the transmission of outgoing serial data to complete.

    Returns:
        None
    """
    __use_as_is__ = False
    __translation__ = "Serial.flush()"
    raise NotImplementedError()


def serial_print(data: str) -> None:
    """
    Prints data to the serial port as human-readable ASCII text.

    Args:
        data (str): The data to send.

    Returns:
        None
    """
    __use_as_is__ = False
    __translation__ = "Serial.print({0})"
    raise NotImplementedError()


def serial_println(data: str) -> None:
    """
    Prints data to the serial port followed by a newline character.

    Args:
        data (str): The data to send.

    Returns:
        None
    """
    __use_as_is__ = False
    __translation__ = "Serial.println({0})"
    raise NotImplementedError()


#################################################################################################


def arduino_bit(n: int) -> int:
    """
    Returns a value with a single bit set.

    Args:
        n (int): Bit position (0 = least significant bit).

    Returns:
        int: A value with the nth bit set (1 << n).
    """
    __use_as_is__ = False
    __translation__ = "bit({0})"
    raise NotImplementedError()


def arduino_bitRead(value: int, bit: int) -> int:
    """
    Reads a specific bit from a value.

    Args:
        value (int): The input integer.
        bit (int): Bit position to read.

    Returns:
        int: 0 or 1, the value of the bit at the given position.
    """
    __use_as_is__ = False
    __translation__ = "bitRead({0}, {1})"
    raise NotImplementedError()


def arduino_bitSet(value: int, bit: int) -> int:
    """
    Sets a specific bit in a value.

    Args:
        value (int): The input integer.
        bit (int): Bit position to set.

    Returns:
        int: Modified value with bit set.
    """
    __use_as_is__ = False
    __translation__ = "bitSet({0}, {1})"
    raise NotImplementedError()


def arduino_bitClear(value: int, bit: int) -> int:
    """
    Clears a specific bit in a value.

    Args:
        value (int): The input integer.
        bit (int): Bit position to clear.

    Returns:
        int: Modified value with bit cleared.
    """
    __use_as_is__ = False
    __translation__ = "bitClear({0}, {1})"
    raise NotImplementedError()


def arduino_bitWrite(value: int, bit: int, bitvalue: int) -> int:
    """
    Writes a 0 or 1 to a specific bit position in a value.

    Args:
        value (int): The input integer.
        bit (int): Bit position to write to.
        bitvalue (int): Either 0 (clear bit) or 1 (set bit).

    Returns:
        int: Modified value.
    """
    __use_as_is__ = False
    __translation__ = "bitWrite({0}, {1}, {2})"
    raise NotImplementedError()


#################################################################################################333


def arduino_lowByte(val: int) -> int:
    """
    Returns the low byte (least significant 8 bits) of a 16-bit value.

    Args:
        val (int): A 16-bit integer.

    Returns:
        int: The lower 8 bits of the input value.
    """
    __use_as_is__ = False
    __translation__ = "lowByte({0})"
    raise NotImplementedError()


def arduino_highByte(val: int) -> int:
    """
    Returns the high byte (most significant 8 bits) of a 16-bit value.

    Args:
        val (int): A 16-bit integer.

    Returns:
        int: The upper 8 bits of the input value.
    """
    __use_as_is__ = False
    __translation__ = "highByte({0})"
    raise NotImplementedError()


#################################################################################


def arduino_random(min_val: int, max_val: int) -> int:
    """
    Generates a random integer between min_val (inclusive) and max_val (exclusive).

    Args:
        min_val (int): Minimum value (inclusive).
        max_val (int): Maximum value (exclusive).

    Returns:
        int: A random integer in the given range.
    """
    __use_as_is__ = False
    __translation__ = "random({0}, {1})"
    raise NotImplementedError()


def arduino_randomSeed(seed: int) -> None:
    """
    Seeds the random number generator with a given seed.

    Args:
        seed (int): The seed value.

    Returns:
        None
    """
    __use_as_is__ = False
    __translation__ = "randomSeed({0})"
    raise NotImplementedError()


##################################################################################################3

############Hardware Serial########################################################################


class HardwareSerial:
    def __init__(self, uart_number: int):
        """
        Reference a hardware serial interface by UART number.

        On most microcontrollers like the ESP32, multiple hardware serial ports are available.
        This class allows selecting one of them using its UART number.

        Args:
            uart_number (int): The UART interface number to use:
                - 0 → Serial
                - 1 → Serial1 (recommended for custom serial devices)
                - 2 → Serial2 (optional, depending on board)

        Notes:
            - UART0 (Serial) is often used for USB or debug logging.
            - UART1 and UART2 are free to use for communicating with sensors like MH-Z19.
            - This stub maps `HardwareSerial(1)` to `Serial1`, and so on.
            - No new object is created — the stub just tells the transpiler to use the named instance.

        Example:
            serial = HardwareSerial(1)      # Refers to Serial1
            sensor = MHZ19Sensor(serial)    # Becomes: create_mhz19(Serial1)
        """
        __use_as_is__ = False
        __class_actual_type__ = "HardwareSerial"
        __translation__ = "({1})"  # emit raw symbol like Serial1
