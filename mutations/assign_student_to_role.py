import graphene

import models
from gql_types import Role, Matchup, Student

class AssignStudentToRole(graphene.Mutation):
  class Arguments:
    tournament_id = graphene.ID(required=True)
    team = graphene.Int(required=True)
    matchup = graphene.ID(required=True)
    student = graphene.ID(required=True)
    role = graphene.Argument(Role, required=True)

  matchup = graphene.Field(Matchup, required=True)
  student = graphene.Field(Student, required=True)
  role = graphene.Field(Role, required=True)

  @staticmethod
  def mutate(parent, info, tournament_id, team, matchup, student, role):
    models.Role.assign_role(tournament_id, matchup, team, student, role)
    return AssignStudentToRole(matchup=Matchup(id=matchup) , student=Student(id=student), role=role)
    # return AssignStudentToRole()