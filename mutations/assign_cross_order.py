import graphene

from gql_types import Side, Matchup, Team, Student
from models import Examination


class AssignCrossOrder(graphene.Mutation):
    class Arguments:
        tournament = graphene.ID(required=True)
        matchup = graphene.ID(required=True)
        side = graphene.Argument(Side, required=True)
        student = graphene.ID(required=True)
        order = graphene.Int(required=True)

    matchup = graphene.Field(Matchup, required=True)
    team = graphene.Field(Team, required=True)
    student = graphene.Field(Student, required=True)
    order = graphene.Int(required=True)

    @staticmethod
    def mutate(parent, info, tournament, matchup, side, student, order):
        Examination.assign_attorney_to_cross(matchup, side, order, student)
        new_matchup = Matchup(id=matchup)
        new_team = Team(num=1101)
        new_student = Student(id=student)
        return AssignCrossOrder(
            matchup=new_matchup, team=new_team, student=new_student, order=order
        )
