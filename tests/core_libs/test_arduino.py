import arduino as ad


def func() -> None:
    pass


def setup() -> None:
    ad.pinMode(13, 1)
    ad.digitalWrite(13, 1)
    ad.digitalRead(13)
    ad.analogRead(1)
    ad.analogWrite(9, 128)
    ad.delay(1000)
    ad.delayMicroseconds(1000)
    ad.millis()
    ad.micros()
    ad.shiftOut(8, 12, 0, 255)
    ad.shiftIn(8, 12, 0)
    ad.pulseIn(7, 1, 1000000)
    ad.tone(9, 1000, 500)
    ad.noTone(9)
    ad.noInterrupts()
    ad.interrupts()
    ad.attachInterrupt(2, func, 3)
    ad.detachInterrupt(2)
    ad.math_min(5, 10)
    ad.math_max(5, 10)
    ad.math_abs(-42)
    ad.math_constrain(150.0, 0.0, 100.0)
    ad.math_map(50.0, 0.0, 100.0, 0.0, 255.0)
    ad.math_pow(2.0, 8.0)
    ad.math_sqrt(16.0)
    ad.math_sq(5.0)
    ad.math_sin(3.14159)
    ad.math_cos(0.0)
    ad.math_tan(0.785)
    ad.math_radians(180.0)
    ad.math_degrees(3.14159)
    ad.math_round(3.7)
    ad.math_ceil(3.2)
    ad.math_floor(3.9)
    ad.math_fmod(10.5, 3.2)
    ad.math_log(2.718)
    ad.math_log10(100.0)
    ad.math_exp(1.0)
    ad.serial_begin(9600)
    ad.serial_end()
    ad.serial_available()
    ad.serial_read()
    ad.serial_peek()
    ad.serial_flush()
    ad.serial_print("Hello")
    ad.serial_println("World")
    ad.arduino_bit(3)
    y = 12
    ad.arduino_bitRead(y, 2)
    z = 8
    ad.arduino_bitSet(z, 1)
    x = 15
    ad.arduino_bitClear(x, 3)
    aa = 1
    ad.arduino_bitWrite(aa, 1, 1)
    ad.arduino_lowByte(256)
    ad.arduino_highByte(256)
    ad.arduino_random(1, 100)
    ad.arduino_randomSeed(42)


def loop() -> None:
    pass
