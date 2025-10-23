__include_modules__ = "GP2Y0A21YK"
__dependencies__ = ""
__include_internal_modules__ = ""


class GP2Y0A21YKSensor:
    def __init__(self):
        """
        Infrared analog distance sensor (Sharp GP2Y0A21YK).
        analog_pin defaults to 36 in ESP32 and A0 in ESP8266.
        """
        __use_as_is__ = False
        __class_actual_type__ = "GP2Y0A21YK"
        __translation__ = ""

    def distance(self) -> float:
        """
        Read and convert analog voltage to approximate distance.

        Returns:
            float: Distance in centimeters.
        """
        __translation__ = "{0}.distance()"
