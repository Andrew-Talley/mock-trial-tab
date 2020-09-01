import graphene


class Role(graphene.Enum):
    WITNESS = "witness"
    ATTORNEY = "attorney"


class ExamType(graphene.Enum):
    DIRECT = "direct"
    CROSS = "cross"


class AttorneyRole(graphene.Enum):
    OPENER = 1
    MIDDLE = 2
    CLOSER = 3


class Side(graphene.Enum):
    PL = "pl"
    DEF = "def"


class Speech(graphene.Enum):
    OPENING = "open"
    CLOSING = "close"
