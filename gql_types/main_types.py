import graphene
from models import School as SQLSchool, Judge as SQLJudge, Matchup as SQLMatchup

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

class Ballot(graphene.ObjectType):
  id = graphene.ID(required=True)
  matchup = graphene.Field(lambda: Matchup, required=True)
  judge = graphene.Field(lambda: Judge, required=True)

class Matchup(graphene.ObjectType):
  id = graphene.ID(required=True)

  pl = graphene.Field(Team, required=True)
  defense = graphene.Field(Team, required=True, name="def")

  @staticmethod
  def resolve_pl(parent, info):
    match = SQLMatchup.get_matchup(parent.id)
    return Team(num=match['pl'])

  @staticmethod
  def resolve_defense(parent, info):
    match = SQLMatchup.get_matchup(parent.id)
    return Team(num=match['def'])

  ballots = graphene.List(Ballot)
  @staticmethod
  def resolve_ballots(parent, info):
    ids = SQLMatchup.get_ballots(parent.id)
    return [Ballot(id=id) for id in ids]

class Judge(graphene.ObjectType):
  id = graphene.ID(required=True)
  name = graphene.String(required=True)

  tournament_id = graphene.ID(required=True)

  ballots = graphene.List(Ballot, required=True)
  @staticmethod
  def resolve_ballots(parent, info):
    ballot_ids = SQLJudge.get_ballots(parent.tournament_id, parent.id)
    return [Ballot(id=id) for id in ballot_ids]

  conflicts = graphene.List(lambda: School, required=True)
  @staticmethod
  def resolve_conflicts(parent, info):
    school_names = SQLJudge.get_conflicts(parent.tournament_id, parent.id)
    return [School(name=name) for name in school_names]
