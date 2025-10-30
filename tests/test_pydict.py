def setup() -> None:
    # simple_test_pydict.py

    print("=== INT values ===")
    d1: dict[str, int] = {}
    d1["a"] = 10
    d1["b"] = -3
    print(d1)
    print(d1["a"], d1["b"])

    print("=== FLOAT values ===")
    d2: dict[str, float] = {}
    d2["pi"] = 3.14
    d2["g"] = 9.81
    print(d2)
    print(d2["pi"], d2["g"])

    print("=== BOOL values ===")
    d3: dict[str, bool] = {}
    d3["flag1"] = True
    d3["flag2"] = False
    print(d3)
    print(d3["flag1"], d3["flag2"])

    print("=== STRING values ===")
    d4: dict[str, str] = {}
    d4["name"] = "Mojoscale"
    d4["lang"] = "C++"
    print(d4)
    print(d4["name"], d4["lang"])

    print("=== BASIC OPERATIONS ===")
    d6: dict[str, int] = {}
    d6["x"] = 100
    print("before pop:", d6)
    v = d6.pop("x")
    print("popped:", v)
    print("after pop:", d6)
    d6["y"] = 200
    d6.clear()
    print("after clear:", d6)


def loop() -> None:
    pass
