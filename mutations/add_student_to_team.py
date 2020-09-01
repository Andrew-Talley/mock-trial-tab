import graphene

from gql_types import Team, Student
import models


class AddStudentToTeam(graphene.Mutation):
    class Arguments:
        tournament_id = graphene.ID(required=True)
        team = graphene.Int(required=True)
        name = graphene.String(required=True)

    team = graphene.Field(Team, required=True)
    student = graphene.Field(Student, required=True)

    @staticmethod
    def mutate(parent, info, tournament_id, team, name):
        new_id = models.Student.add_student(tournament_id, team, name)

        new_team = Team(num=team, tournament_id=tournament_id)
        new_student = Student(id=new_id)
        return AddStudentToTeam(team=new_team, student=new_student)
