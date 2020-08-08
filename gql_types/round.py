import graphene
from gql_types.school import Matchup

class Round(graphene.ObjectType):
  round_num = graphene.Int(required=True)

  matchups = graphene.List(Matchup, required=True)