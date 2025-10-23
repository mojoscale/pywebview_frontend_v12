import onewire as ow

onewire = ow.OneWire(2)


def setup() -> None:
    onewire.reset()
    onewire.write(1, True)
    onewire.write_bytes(1, True)

    read_value = onewire.read()

    read_bytes_values = onewire.read_bytes(3)


def loop() -> None:
    pass
