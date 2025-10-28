def setup() -> None:
    # Simple PyList-style tests (compile check only)

    # Integer list
    int_list = [1, 2, 3]
    int_list.append(4)
    int_list.pop()
    int_list.insert(1, 99)
    int_list.remove(2)
    int_list.extend([5, 6])
    int_list.reverse()
    int_list.sort()
    int_list.clear()
    print("int_list:", int_list)

    # Float list
    float_list = [1.1, 2.2, 3.3]
    float_list.append(4.4)
    float_list.pop()
    float_list.insert(0, 0.5)
    float_list.remove(2.2)
    float_list.extend([5.5, 6.6])
    float_list.reverse()
    float_list.sort()
    print("float_list:", float_list)

    # String list
    str_list = ["apple", "banana", "cherry"]
    str_list.append("date")
    str_list.pop()
    str_list.insert(1, "blueberry")
    str_list.remove("banana")
    str_list.extend(["elderberry", "fig"])
    str_list.reverse()
    str_list.sort()
    print("str_list:", str_list)

    # Boolean list
    bool_list = [True, False, True]
    bool_list.append(False)
    bool_list.pop()
    bool_list.insert(1, True)
    bool_list.remove(False)
    bool_list.extend([True, False])
    bool_list.reverse()
    # sorting booleans also works (False < True)
    bool_list.sort()
    print("bool_list:", bool_list)

    # Slice, copy, and concatenation
    a = [1, 2, 3]
    b = [4, 5]
    c = a + b
    d = a.copy()
    e = a[1:3]
    print("combined:", c)
    print("copy:", d)
    print("slice:", e)

    # Repetition
    f = a * 3
    print("repeated:", f)


def loop() -> None:
    pass
