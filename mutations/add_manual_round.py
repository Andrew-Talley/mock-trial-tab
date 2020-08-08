import graphene

from gql_types import Round, Matchup, Team

from models import Matchup as SQLMatchup

class ManualRoundMatchup(graphene.InputObjectType):
  pl = graphene.Int(required=True)
  defense = graphene.Int(required=True, name="def")

class AddManualRound(graphene.Mutation):
  class Arguments:
    tournament_id = graphene.ID(required=True)
    matchups = graphene.List(ManualRoundMatchup, required=True)

  Output = graphene.NonNull(Round)

  @staticmethod
  def mutate(parent, info, tournament_id, matchups):
    current_round = 1

    for matchup in matchups:
      SQLMatchup.add_matchup(tournament_id, round_num=current_round, pl=matchup['pl'], defense=matchup['defense'])
    return Round(round_num=1, matchups=[Matchup(pl=Team(num=1001), defense=Team(num=1101)), Matchup(pl=Team(num=1002), defense=Team(num=1102))])
