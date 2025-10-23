import wire as w


# Define simple callback functions
def my_receive_handler(num_bytes: int) -> None:
    print(f"Received {num_bytes} bytes")
    for i in range(num_bytes):
        data = read()
        print(f"Byte {i}: {data}")


def my_request_handler() -> None:
    print("Master requested data")


def setup() -> None:
    # Call all the functions
    w.begin(0x08)
    w.begin_transmission(0x50)
    w.write(0x10)
    w.write(0x20)
    result = w.end_transmission(True)

    bytes_available = w.request_from(0x50, 6, True)
    data = w.read()
    count = w.available()

    on_receive(my_receive_handler)
    on_request(my_request_handler)


def loop() -> None:
    pass
