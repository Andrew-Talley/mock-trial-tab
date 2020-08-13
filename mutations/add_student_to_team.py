import graphene

from gql_types import Team, Student
import models


class AddStudentToTeam(graphene.Mutation):
    class Arguments:
        tournament_id = graphene.ID(required=True)
        team = graphene.Int(required=True)
        name = graphene.String(required=True)

    Output = Team

    @staticmethod
    def mutate(parent, info, tournament_id, team, name):
        models.Student.add_student(tournament_id, team, name)
        return Team(num=team, tournament_id=tournament_id)
