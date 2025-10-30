def setup() -> None:
    a = 5
    b = 3

    n2 = a + b
    n3 = a - b
    n4 = a * b
    n5 = a / b
    test = a % b
    n6 = -a

    a == b
    a != b
    a < b
    a <= b
    a > b
    a >= b

    t2 = a.bit_length()
    t3 = a.bit_count()
    t4 = a.numerator()
    t5 = a.denominator()
    t6 = a.is_integer()
    t7 = a.real()
    t8 = a.imag()
    t9 = a.conjugate()
    num = 0
    denom = 0

    s = a.to_bytes()

    a.print()


def loop() -> None:
    pass
