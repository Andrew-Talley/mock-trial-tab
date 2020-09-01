import graphene

from gql_types import Matchup, Student, Side
from models import Examination


class AssignWitnessOrder(graphene.Mutation):
    class Arguments:
        tournament = graphene.ID(required=True)
        matchup = graphene.ID(required=True)
        side = graphene.Argument(Side, required=True)
        student = graphene.ID(required=True)
        order = graphene.Int(required=True)

    matchup = graphene.Field(Matchup, required=True)
    student = graphene.Field(Student, required=True)
    order = graphene.Int(required=True)

    @staticmethod
    def mutate(parent, info, tournament, matchup, side, student, order):
        Examination.assign_student_to_witness_order(matchup, side, order, student)
        return AssignWitnessOrder(
            matchup=Matchup(id=matchup), student=Student(id=student), order=1
        )
