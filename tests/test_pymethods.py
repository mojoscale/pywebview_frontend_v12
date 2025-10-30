def setup() -> None:
    print("=== py_int ===")
    print(int(42))
    print(int(3.9))
    print(int(True))
    print(int("56"))
    print(int("123.9".split(".")[0]))

    print("=== py_float ===")
    print(float(42))
    print(float("3.14"))
    print(float(True))
    print(float(0))

    print("=== py_bool ===")
    print(bool(0))
    print(bool(42))
    print(bool(""))
    print(bool("hello"))

    print("=== py_str ===")
    print(str(123))
    print(str(3.14159))
    print(str(True))
    print(str(False))
    print(str("test"))

    print("=== py_abs ===")
    print(abs(-10))
    print(abs(5))
    print(abs(-3.2))
    print(abs(True))

    print("=== py_bin ===")
    for n in [0, 5, -5, 8]:
        print(bin(n))

    print("=== py_chr / py_ord ===")
    for n in [65, 97, 48]:
        print(chr(n), ord(chr(n)))

    print("=== py_divmod ===")
    print(divmod(10, 3))
    print(divmod(10, -3))

    print("=== py_hex ===")
    for n in [0, 10, 255, -255]:
        print(hex(n))

    print("=== py_len ===")
    print(len("hello"))
    print(len([1, 2, 3]))

    print("=== py_list ===")
    print(list("abc"))
    print(list("1234"))

    print("=== py_oct ===")
    for n in [0, 8, -8, 64]:
        print(oct(n))

    print("=== py_pow ===")
    print(pow(2, 3))
    print(pow(2, 3, 5))
    print(pow(2.5, 2))

    print("=== py_reversed ===")
    print(list(reversed([1, 2, 3])))
    print("".join(reversed("hello")))

    print("=== py_round ===")
    print(round(3.4))
    print(round(3.6))
    print(round(-2.5))
    print(round(5.0))

    print("=== py_sorted ===")
    print(sorted([3, 1, 2]))
    print("".join(sorted("cab")))

    print("=== py_sum ===")
    print(sum([1, 2, 3]))
    print(sum([3.5, 2.5]))

    print("=== concat_all ===")
    print("".join(["Hello", " ", "World"]))
    print("".join(["Pi=", str(3.14)]))


def loop() -> None:
    pass
