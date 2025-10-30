def fromString(s: str) -> bool:
    return s in ["True", "true", "1"]


def from_bytes(s: str) -> bool:
    return len(s) > 0 and s[0] != 0


def to_bytes(v: bool) -> str:
    if v:
        return "1"
    return "0"


def setup() -> None:
    print("=== Constructors ===")
    a = bool()
    b = bool(True)
    c = bool(0)
    d = bool(1)

    test_str = "assd"
    test_bool_list = [True, False, True]
    print(a, b, c, d)

    print("=== Logical ops ===")
    print("!True ->", not True)
    print("True == True ->", True == True)
    print("True != False ->", True != False)
    print("True && False ->", True and False)

    print("True || False ->", True or False)

    print("=== Conversions ===")
    print("bool(1):", bool(1))
    print("bool(0):", bool(0))

    print("=== Toggle (manual) ===")
    x = True
    print("Before toggle:", x)
    x = not x
    print("After toggle:", x)

    print(fromString("True"), fromString("false"), fromString("1"), fromString("0"))

    print("=== bit_length / bit_count / numerator / denominator ===")
    for v in [False, True]:
        print(f"{v}: bit_length={v}, bit_count={v}, numerator={v}, denominator=1")

    for v in [False, True]:
        b1 = to_bytes(v)
        f = from_bytes(b1)
        print(f"{v} -> bytes={b} -> back={f}")


def loop() -> None:
    pass
