def setup() -> None:
    print("=== PyString Tests ===")

    s1 = "hello world"
    s2 = "HELLO"
    s3 = "12345"
    s4 = "   spaced   "
    s5 = "python rocks"

    print(s1)
    print(len(s1))
    print(s1[1])
    print(s1.lower())
    print(s1.upper())
    print(s1.capitalize())
    print(s5.title())
    print(s1.swapcase())

    print(s4.strip())
    print(s4.lstrip())
    print(s4.rstrip())

    print(s1.replace("world", "Python"))
    print(s1.replace("l", "L"))
    print(s1.startswith("he"))
    print(s1.endswith("ld"))
    print(s1.count("l"))
    print(s1.find("l"))
    print(s1.rfind("l"))
    print("Contains 'world':", "world" in s1)

    print(s3.isnumeric(), s3.isdigit(), s3.isdecimal())
    print(s2.isupper(), s1.islower(), s5.isalpha(), s3.isalnum())
    print("   ".isspace())

    print("Remove prefix:", "foobar".removeprefix("foo"))
    print("Remove suffix:", "foobar".removesuffix("bar"))
    print("ljust:", s1.ljust(15, "-"))
    print("rjust:", s1.rjust(15, "-"))
    print("zfill:", s3.zfill(8))
    print("slice:", s1[2:8])

    parts = s1.split()
    print(parts)
    joined = "-".join(parts)
    print(joined)

    parts2 = s1.split("o")
    print(parts2)
    joined2 = "o".join(parts2)
    print(joined2)

    print("rsplit:", "a,b,c".rsplit(","))

    # Nesting: pass outputs between functions
    res = "-".join(s1.split())
    print(res)
    res2 = res.upper().replace("-", " ")
    print(res2)

    print("All done..")


def loop() -> None:
    pass
