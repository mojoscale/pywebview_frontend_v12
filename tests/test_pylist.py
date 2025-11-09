def setup() -> None:
    # Simple PyList-style tests (compile check only)

    # Integer list
    int_list = [1, 2, 3]
    print("start int_list:", int_list)
    int_list.append(4)
    print("after append:", int_list)
    int_list.pop()
    print("after pop:", int_list)
    int_list.insert(1, 99)
    print("after insert:", int_list)
    int_list.remove(2)
    print("after remove:", int_list)
    int_list.extend([5, 6])
    print("after extend:", int_list)
    int_list.reverse()
    print("after reverse:", int_list)
    int_list.sort()
    print("after sort:", int_list)
    int_list.clear()
    print("after clear:", int_list)
    print("int_list final:", int_list)

    # Float list
    float_list = [1.1, 2.2, 3.3]
    print("start float_list:", float_list)
    float_list.append(4.4)
    print("after append:", float_list)
    float_list.pop()
    print("after pop:", float_list)
    float_list.insert(0, 0.5)
    print("after insert:", float_list)
    float_list.remove(2.2)
    print("after remove:", float_list)
    float_list.extend([5.5, 6.6])
    print("after extend:", float_list)
    float_list.reverse()
    print("after reverse:", float_list)
    float_list.sort()
    print("after sort:", float_list)
    print("float_list final:", float_list)

    # String list
    str_list = ["apple", "banana", "cherry"]
    print("start str_list:", str_list)
    str_list.append("date")
    print("after append:", str_list)
    str_list.pop()
    print("after pop:", str_list)
    str_list.insert(1, "blueberry")
    print("after insert:", str_list)
    str_list.remove("banana")
    print("after remove:", str_list)
    str_list.extend(["elderberry", "fig"])
    print("after extend:", str_list)
    str_list.reverse()
    print("after reverse:", str_list)
    str_list.sort()
    print("after sort:", str_list)
    print("str_list final:", str_list)

    # Boolean list
    bool_list = [True, False, True]
    print("start bool_list:", bool_list)
    bool_list.append(False)
    print("after append:", bool_list)
    bool_list.pop()
    print("after pop:", bool_list)
    bool_list.insert(1, True)
    print("after insert:", bool_list)
    bool_list.remove(False)
    print("after remove:", bool_list)
    bool_list.extend([True, False])
    print("after extend:", bool_list)
    bool_list.reverse()
    print("after reverse:", bool_list)
    # sorting booleans also works (False < True)
    bool_list.sort()
    print("after sort:", bool_list)
    print("bool_list final:", bool_list)

    # Slice, copy, and concatenation
    a = [1, 2, 3]
    print("start a:", a)
    b = [4, 5]
    print("start b:", b)
    c = a + b
    print("combined (a + b):", c)
    d = a.copy()
    print("copy of a:", d)
    e = a[1:3]
    print("slice of a[1:3]:", e)

    # Repetition
    f = a * 3
    print("repeated (a * 3):", f)


def loop() -> None:
    pass
