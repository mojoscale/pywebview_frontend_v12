# Simple test for PyDictItems-like behavior in Python


def setup() -> None:
    print("=== Testing PyDictItems ===")

    # Simulate the underlying PyDict
    d = {"a": 1, "b": 2, "c": 3}

    # Size
    print("Size:", len(d))  # Expected 3

    # Keys and values by index
    keys = list(d.keys())
    print("Key[0]:", keys[0])
    print("Value[0]:", d[keys[0]])

    # Iterate manually (like begin()/end())
    print("Iterating:")
    for k, v in d.items():
        print(f"{k}, {v}")

    print("All tests done ")


def loop() -> None:
    pass
