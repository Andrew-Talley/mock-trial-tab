import graphene

from gql_types import Side, Matchup, Student
import models


class AssignAttorneyToDirect(graphene.Mutation):
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
        models.Examination.assign_attorney_to_direct_order(
            matchup, side, order, student
        )
        new_matchup = Matchup(id=matchup)
        new_student = Student(id=student)
        return AssignAttorneyToDirect(
            matchup=new_matchup, student=new_student, order=order
        )
