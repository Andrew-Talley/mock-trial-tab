import graphene
from graphene import NonNull
from tab_rounds.generate_round.utilities import Side
from gql_types import School, Team, Tournament, Judge, Round

from mutations import Mutation

from models.tournament import Tournament as SQLTournament
from models.school import School as SQLSchool
from models.team import Team as SQLTeam
from models.judge import Judge as SQLJudge


class TournamentQuery:
    tournament = graphene.Field(
        Tournament,
        args={"id": graphene.Argument(graphene.ID, required=True)},
        required=True,
    )

    @staticmethod
    def resolve_tournament(parent, info, id):
        return Tournament(id=id)


class TournamentsQuery:
    tournaments = graphene.Field(graphene.List(Tournament), required=True)

    @staticmethod
    def resolve_tournaments(parent, info):
        tournaments = SQLTournament.get_all_tournaments()
        return [
            Tournament(id=tournament["id"], name=tournament["name"])
            for tournament in tournaments
        ]


class Query(graphene.ObjectType, TournamentQuery, TournamentsQuery):
    pass


schema = graphene.Schema(query=Query, mutation=Mutation)
