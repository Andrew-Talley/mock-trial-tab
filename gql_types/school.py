import graphene
from models import School as SQLSchool

class School(graphene.ObjectType):
  tournament_id = graphene.ID()
  name = graphene.String()

  teams = graphene.List(lambda: Team)

  @staticmethod
  def resolve_teams(parent, info):
    teams = SQLSchool.get_teams_for_school(parent.tournament_id, parent.name)
    return [Team(num=team['num'], name=team['name']) for team in teams]

class Team(graphene.ObjectType):
  name = graphene.String(required=True)
  num = graphene.Int(required=True)

  school_name = graphene.String(required=True)
  school = graphene.NonNull(School)

  tournament_id = graphene.ID(required=True)

class Matchup(graphene.ObjectType):
  pl = graphene.Field(Team, required=True)
  defense = graphene.Field(Team, required=True, name="def")