__include_modules__ = "PedestrianDetector"
__include_internal_modules__ = ""
__dependencies__ = "eloquentarduino/EloquentTinyML"
__available_platforms__ = ""
__embed_files__ = ""


class PedestrianDetector:
    def __init__(self):
        __translation__ = ""
        __construct_with_equal_to__ = False

    def begin(self) -> None:
        __translation__ = "{self}.begin()"

    def detect(self, image: Image) -> bool:
        __translation__ = "{self}.detect({image})"
