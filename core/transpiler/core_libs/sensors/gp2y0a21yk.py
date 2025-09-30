__include_modules__ = "GP2Y0A21YK"
__dependencies__ = "volty98/GP2Y0A21YK_lib"


class GP2Y0A21YKSensor:
    def __init__(self, analog_pin: int):
        """
        Infrared analog distance sensor (Sharp GP2Y0A21YK).

        Args:
            analog_pin (int): Analog pin used for reading the voltage (default A3, i.e., 17).
        """
        __use_as_is__ = False
        __class_actual_type__ = "GP2Y0A21YK"
        __translation__ = "({1})"

    def distance(self) -> float:
        """
        Read and convert analog voltage to approximate distance.

        Returns:
            float: Distance in centimeters.
        """
        __translation__ = "{0}.distance()"
