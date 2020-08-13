import graphene


class Role(graphene.Enum):
    OPENER = 1
    MIDDLE = 2
    CLOSER = 3
