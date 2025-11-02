import comms.ble_simple as b


def on_write_handler(value: str) -> None:
    print("Central wrote:", value)


def setup() -> None:
    # Create BLE instance in peripheral mode
    ble = b.BLESimple("MyDevice", mode="peripheral")

    # Initialize BLE
    ble.init_ble()

    # Add service and characteristic
    ble.add_service("1234")
    ble.add_characteristic(
        "1234",  # service UUID
        "5678",  # characteristic UUID
        "Hello",  # default value
    )

    # Start advertising
    ble.start()

    # Example callback registration

    ble.on_write("5678", on_write_handler)

    # Optional: call other methods just to verify transpilation

    ble.is_connected()
    ble.get_services()
    ble.get_characteristics("1234")


def loop() -> None:
    # Nothing here for now
    pass
