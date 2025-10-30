# Simple manual test for PyRange behavior


def setup() -> None:
    print("=== Testing PyRange ===")

    # Test 1: Single argument (stop)
    r1 = range(5)
    print("r1:", list(r1))  # Expected [0, 1, 2, 3, 4]

    # Test 2: start, stop
    r2 = range(2, 6)
    print("r2:", list(r2))  # Expected [2, 3, 4, 5]

    # Test 3: start, stop, step
    r3 = range(1, 10, 3)
    print("r3:", list(r3))  # Expected [1, 4, 7]

    # Test 4: negative step
    r4 = range(10, 0, -3)
    print("r4:", list(r4))  # Expected [10, 7, 4, 1]

    # Test 5: indexing
    r5 = range(3, 9, 2)
    print("r5[0]:", r5[0])  # 3
    print("r5[1]:", r5[1])  # 5
    print("r5[2]:", r5[2])  # 7

    # Test 6: length
    print("len(r5):", len(r5))  # 3


def loop() -> None:
    pass
