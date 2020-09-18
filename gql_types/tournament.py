import graphene

from models import Tournament as SQLTournament, Judge as SQLJudge, Team as SQLTeam

from gql_types.main_types import School, Team, Judge, Matchup, Ballot
from gql_types.round import Round


class Tournament(graphene.ObjectType):
    id = graphene.ID(required=True)
    name = graphene.String(required=True)

    schools = graphene.List(graphene.NonNull(School), required=True)

    @staticmethod
    def resolve_name(parent, info):
        return SQLTournament.get_all_info_for_tournament(parent.id)['name']

    @staticmethod
    def resolve_schools(parent, info):
        schools_info = SQLTournament.get_schools_for_tournament(parent.id)
        schools = [
            School(tournament_id=school["tournament_id"], name=school["name"])
            for school in schools_info
        ]
        return schools

    teams = graphene.List(graphene.NonNull(Team), required=True)

    @staticmethod
    def resolve_teams(parent, info):
        teams = SQLTournament.get_teams_for_tournament(parent.id)
        return [
            Team(
                tournament_id=parent.id,
                num=team["num"],
                name=team["name"],
                school_name=team["school_name"],
            )
            for team in teams
        ]

    team = graphene.Field(
        Team,
        args={"num": graphene.Argument(graphene.Int, required=True)},
        required=True,
    )

    @staticmethod
    def resolve_team(parent, info, num):
        return Team(tournament_id=parent.id, num=num,)

    school = graphene.Field(
        School,
        args={"name": graphene.Argument(graphene.String, required=True)},
        required=True,
    )

    @staticmethod
    def resolve_school(parent, info, name):
        return School(tournament_id=parent.id, name=name)

    judges = graphene.List(Judge, required=True)

    @staticmethod
    def resolve_judges(parent, info):
        judges = SQLTournament.get_judges_for_tournament(parent.id)
        return [Judge(id=judge["id"], name=judge["name"]) for judge in judges]

    judge = graphene.Field(
        Judge, args={"id": graphene.Argument(graphene.ID, required=True)}, required=True
    )

    @staticmethod
    def resolve_judge(parent, info, id):
        judge = SQLJudge.get_judge(parent.id, id)
        return Judge(id=judge["id"], name=judge["name"], tournament_id=parent.id)

    rounds = graphene.List(graphene.NonNull(Round), required=True)

    @staticmethod
    def resolve_rounds(parent, info):
        rounds = SQLTournament.get_all_rounds(parent.id)
        return [
            Round(round_num=round_num, tournament_id=parent.id) for round_num in rounds
        ]

    single_round = graphene.Field(
        Round,
        args={"num": graphene.Argument(graphene.Int, required=True)},
        required=True,
        name="round",
    )

    @staticmethod
    def resolve_single_round(parent, info, num):
        return Round(round_num=num, tournament_id=parent.id)

    matchup = graphene.Field(
        Matchup,
        required=True,
        args={"id": graphene.Argument(graphene.ID, required=True)},
    )

    @staticmethod
    def resolve_matchup(parent, info, id):
        return Matchup(id=id)

    ballot = graphene.Field(
        Ballot, args={"id": graphene.ID(required=True)}, required=True
    )

    @staticmethod
    def resolve_ballot(parent, info, id):
        return Ballot(id=id)
