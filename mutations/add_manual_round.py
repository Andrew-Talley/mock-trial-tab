import graphene

from gql_types import Round, Matchup, Team

from models import Matchup as SQLMatchup, Tournament as SQLTournament


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
        existing_rounds = SQLTournament.get_all_rounds(tournament_id)
        current_round = len(existing_rounds) + 1

        for matchup in matchups:
            SQLMatchup.add_matchup(
                tournament_id,
                round_num=current_round,
                pl=matchup["pl"],
                defense=matchup["defense"],
            )
        return Round(round_num=current_round, tournament_id=tournament_id)
