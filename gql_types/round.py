import graphene
from gql_types.main_types import Matchup, Team

from models import Round as SQLRound


class Round(graphene.ObjectType):
    tournament_id = graphene.ID(required=True)
    round_num = graphene.Int(required=True)

    matchups = graphene.List(Matchup, required=True)

    @staticmethod
    def resolve_matchups(parent, info):
        matchups = SQLRound.get_matchups_for_round(
            parent.tournament_id, parent.round_num
        )
        return [
            Matchup(
                id=matchup["id"],
                pl=Team(num=matchup["pl"]),
                defense=Team(num=matchup["def"]),
            )
            for matchup in matchups
        ]
