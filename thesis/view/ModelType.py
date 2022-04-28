from enum import Enum


class ModelType(Enum):
    """
    An enum class responsible for describing the type of the membrane system

    Currently there are two types supported
    """

    BASE = 0
    SYMPORT = 1
