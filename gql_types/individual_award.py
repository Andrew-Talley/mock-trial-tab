import graphene
from .main_types import Student
from .enums import Side, Role


class IndividualAward(graphene.ObjectType):
    side = graphene.Field(Side, required=True)
    ranks = graphene.Int(required=True)
    role = graphene.Field(Role, required=True)

    student = graphene.Field(Student, required=True)
