import hardware_serial as hs


def setup() -> None:
    # create Serial1 instance and begin communication
    serial1 = hs.HardwareSerial(1)
    serial1.begin(115200, 2)

    # basic writes
    serial1.print("Hello, world")
    serial1.println("from HardwareSerial test")
    serial1.write(65)  # ASCII 'A'

    # flush to ensure data sent
    serial1.flush()


def loop() -> None:
    pass
