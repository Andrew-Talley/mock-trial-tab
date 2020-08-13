import graphene
from graphene import NonNull

import models
from models import (
    School as SQLSchool,
    Judge as SQLJudge,
    Matchup as SQLMatchup,
    Team as SQLTeam,
)

from gql_types.role import Role


class School(graphene.ObjectType):
    tournament_id = graphene.ID()
    name = graphene.String()

    teams = graphene.List(lambda: Team)

    @staticmethod
    def resolve_teams(parent, info):
        teams = SQLSchool.get_teams_for_school(parent.tournament_id, parent.name)
        return [
            Team(tournament_id=parent.tournament_id, num=team["num"], name=team["name"])
            for team in teams
        ]


class Team(graphene.ObjectType):
    name = graphene.String(required=True)

    def resolve_name(parent, info):
        try:
            return parent.name
        except:
            team = SQLTeam.get_team(parent.tournament_id, parent.num)
            return team["name"]

    num = graphene.Int(required=True)

    school_name = graphene.String(required=True)
    school = NonNull(School)

    tournament_id = graphene.ID(required=True)

    students = NonNull(graphene.List(lambda: Student, required=True))

    @staticmethod
    def resolve_students(parent, info):
        students = models.Team.get_students(parent.tournament_id, parent.num)
        return [Student(id=student["id"], name=student["name"]) for student in students]


class Student(graphene.ObjectType):
    id = graphene.ID(required=True)
    name = graphene.String(required=True)


class Ballot(graphene.ObjectType):
    id = graphene.ID(required=True)
    matchup = graphene.Field(lambda: Matchup, required=True)
    judge = graphene.Field(lambda: Judge, required=True)


class MatchupTeam(graphene.ObjectType):
    tournament_id = graphene.ID(required=True)
    matchup_id = graphene.ID(required=True)
    team_num = graphene.Int(required=True)

    team = graphene.Field(Team, required=True)

    @staticmethod
    def resolve_team(parent, info):
        return Team(num=parent.team_num)

    student_in_role = graphene.Field(
        Student, args={"role": graphene.Argument(Role, required=True)}
    )

    @staticmethod
    def resolve_student_in_role(parent, info, role):
        student_id = models.Role.get_student_in_role(
            parent.tournament_id, parent.matchup_id, parent.team_num, role
        )
        return Student(id=student_id)


class Matchup(graphene.ObjectType):
    id = graphene.ID(required=True)

    pl = graphene.Field(MatchupTeam, required=True)
    defense = graphene.Field(MatchupTeam, required=True, name="def")

    @staticmethod
    def resolve_pl(parent, info):
        match = SQLMatchup.get_matchup(parent.id)
        t_id, p_id = match.get("tournament_id"), match.get("pl")
        return MatchupTeam(
            team_num=match["pl"], tournament_id=t_id, matchup_id=parent.id
        )

    @staticmethod
    def resolve_defense(parent, info):
        match = SQLMatchup.get_matchup(parent.id)
        t_id, d_id = match.get("tournament_id"), match.get("def")
        return MatchupTeam(team_num=d_id, tournament_id=parent.id, matchup_id=parent.id)

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
