__include_modules__ = "SoftwareSerial"
__dependencies__ = "SoftwareSerial"


class SoftwareSerial:
    def __init__(self, rx: int, tx: int):
        """
        Create a software serial interface on given GPIO pins.

        Args:
            rx (int): GPIO pin for RX
            tx (int): GPIO pin for TX
        """
        __use_as_is__ = False
        __class_actual_type__ = "SoftwareSerial"
        __translation__ = "({1}, {2})"
