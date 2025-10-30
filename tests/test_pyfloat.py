def setup() -> None:
    a = 3.5
    b = 2.0

    a.get()
    a + b
    a - b
    a * b
    a / b
    a % b
    -a

    a == b
    a != b
    a < b
    a <= b
    a > b
    a >= b

    t1 = a.pow(b)
    t2 = a.is_integer()
    num = 0
    denom = 2
    t3 = a.as_integer_ratio()
    t4 = a.hex()
    t5 = a.round()
    a.print()
    t7 = a.str()
    t8 = a.real()
    t9 = a.imag()
    t10 = a.conjugate()
    t11 = a.bit_length()
    t12 = a.bit_count()
    s = a.to_bytes()


def loop() -> None:
    pass
