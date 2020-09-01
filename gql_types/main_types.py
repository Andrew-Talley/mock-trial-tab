from __future__ import annotations
import graphene
from graphene import NonNull

import models

from gql_types.enums import Role, AttorneyRole, Side, Speech, ExamType


class School(graphene.ObjectType):
    tournament_id = graphene.ID()
    name = graphene.String()

    teams = graphene.List(lambda: Team)

    @staticmethod
    def resolve_teams(parent, info):
        teams = models.School.get_teams_for_school(parent.tournament_id, parent.name)
        return [
            Team(tournament_id=parent.tournament_id, num=team["num"], name=team["name"])
            for team in teams
        ]


class Team(graphene.ObjectType):
    name = graphene.String(required=True)

    def resolve_name(parent, info):
        return parent.name

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

    @staticmethod
    def resolve_name(parent, info):
        student = models.Student.get_student(parent.id)
        return student["name"]


class BallotSide(graphene.ObjectType):
    side = graphene.Field(Side, required=True)
    speech = graphene.Int(args={"speech": graphene.Argument(Speech, required=True)})
    exam = graphene.Int(
        args={
            "order": graphene.Int(required=True),
            "role": graphene.Argument(Role, required=True),
            "exam_type": graphene.Argument(ExamType, required=True, name="type"),
        },
    )

    side_sum = graphene.Int(required=True, name="sum")

    _ballot: Ballot = None

    @staticmethod
    def resolve_speech(parent, info, speech):
        return models.Scores.get_speech_score(parent._ballot.id, parent.side, speech)[
            "score"
        ]

    @staticmethod
    def resolve_exam(parent, info, order, role, exam_type):
        return models.Scores.get_exam_score(
            parent._ballot.id, parent.side, order, role, exam_type
        )["score"]

    @staticmethod
    def resolve_side_sum(parent, info):
        return models.Scores.get_sum(parent._ballot.id, parent.side)


class Ballot(graphene.ObjectType):
    id = graphene.ID(required=True)
    matchup = graphene.Field(lambda: Matchup, required=True)
    judge = graphene.Field(lambda: Judge, required=True)

    side = graphene.Field(
        BallotSide, args={"side": graphene.Argument(Side, required=True)}, required=True
    )

    pd = graphene.Int(
        required=True, args={"side": graphene.Argument(Side, required=True)}
    )

    complete = graphene.Boolean(required=True)

    @staticmethod
    def resolve_side(parent, info, side):
        ballot_side = BallotSide(side=side)
        ballot_side._ballot = parent
        return ballot_side

    @staticmethod
    def resolve_pd(parent, info, side):
        pl_sum = models.Scores.get_sum(parent.id, Side.PL)
        def_sum = models.Scores.get_sum(parent.id, Side.DEF)

        pl_pd = pl_sum - def_sum

        if side == Side.PL:
            return pl_pd
        else:
            return -pl_pd

    @staticmethod
    def resolve_complete(parent, info):
        return models.Ballot.get_is_complete(parent.id)


class MatchupWitness(graphene.ObjectType):
    matchup_team = graphene.Field(lambda: MatchupTeam, required=True)
    order = graphene.Int(required=True)
    student = graphene.Field(Student, required=True)
    witness_name = graphene.String(required=True)

    @staticmethod
    def resolve_student(parent, info):
        student_id = models.Examination.get_witness_in_order(
            parent.matchup_team.matchup_id, parent.matchup_team.side, parent.order
        )
        return Student(id=student_id)

    @staticmethod
    def resolve_witness_name(parent, info):
        return models.Examination.get_witness_name(
            parent.matchup_team.matchup_id, parent.matchup_team.side, parent.order
        )


class MatchupAttorney(graphene.ObjectType):
    student = graphene.Field(Student, required=True)


class MatchupTeam(graphene.ObjectType):
    tournament_id = graphene.ID(required=True)
    matchup_id = graphene.ID(required=True)
    team_num = graphene.Int(required=True)
    side = graphene.Field(Side, required=True)

    team = graphene.Field(Team, required=True)

    @staticmethod
    def resolve_team(parent, info):
        return Team(num=parent.team_num)

    student_in_role = graphene.Field(
        Student, args={"role": graphene.Argument(AttorneyRole, required=True)}
    )

    @staticmethod
    def resolve_student_in_role(parent, info, role):
        student_id = models.Role.get_student_in_role(
            parent.tournament_id, parent.matchup_id, parent.team_num, role
        )
        return Student(id=student_id)

    witness = graphene.Field(
        MatchupWitness, args={"order": graphene.Int()}, required=True
    )

    @staticmethod
    def resolve_witness(parent, info, order):
        return MatchupWitness(order=order, matchup_team=parent)

    attorney = graphene.Field(
        MatchupAttorney,
        args={
            "order": graphene.Int(),
            "role": graphene.Argument(AttorneyRole),
            "crossing_witness_num": graphene.Int(),
        },
    )

    @staticmethod
    def resolve_attorney(parent, info, **kwargs):
        role = kwargs.get("role", None)
        if role is not None:
            student_id = models.Role.get_student_in_role(
                parent.tournament_id, parent.matchup_id, parent.team_num, role
            )
            return MatchupAttorney(student=Student(id=student_id))

        order = kwargs.get("order", None)
        if order is not None:
            attorney_id = models.Examination.get_attorney_in_order(
                parent.matchup_id, parent.side, order
            )
            return MatchupAttorney(student=Student(id=attorney_id))

        crossing_wit = kwargs.get("crossing_witness_num")
        if crossing_wit is not None:
            attorney_id = models.Examination.get_attorney_crossing_witness(
                parent.matchup_id, parent.side, crossing_wit
            )
            return MatchupAttorney(student=Student(id=attorney_id))


class Matchup(graphene.ObjectType):
    id = graphene.ID(required=True)

    pl = graphene.Field(MatchupTeam, required=True)
    defense = graphene.Field(MatchupTeam, required=True, name="def")

    @staticmethod
    def resolve_pl(parent, info):
        match = models.Matchup.get_matchup(parent.id)
        t_id, p_id = match.get("tournament_id"), match.get("pl")
        return MatchupTeam(
            team_num=match["pl"], tournament_id=t_id, matchup_id=parent.id
        )

    @staticmethod
    def resolve_defense(parent, info):
        match = models.Matchup.get_matchup(parent.id)
        t_id, d_id = match.get("tournament_id"), match.get("def")
        return MatchupTeam(team_num=d_id, tournament_id=t_id, matchup_id=parent.id)

    team = graphene.Field(
        MatchupTeam,
        required=True,
        args={"side": graphene.Argument(Side, required=True)},
    )

    @staticmethod
    def resolve_team(parent, info, side):
        match = models.Matchup.get_matchup(parent.id)
        tourn_id, team_id = match.get("tournament_id"), match.get(side)
        return MatchupTeam(
            team_num=team_id, tournament_id=tourn_id, matchup_id=parent.id, side=side
        )

    ballots = graphene.List(Ballot)

    @staticmethod
    def resolve_ballots(parent, info):
        ids = models.Matchup.get_ballots(parent.id)
        return [Ballot(id=id) for id in ids]


class Judge(graphene.ObjectType):
    id = graphene.ID(required=True)
    name = graphene.String(required=True)

    tournament_id = graphene.ID(required=True)

    ballots = graphene.List(Ballot, required=True)

    @staticmethod
    def resolve_ballots(parent, info):
        ballot_ids = models.Judge.get_ballots(parent.tournament_id, parent.id)
        return [Ballot(id=id) for id in ballot_ids]

    conflicts = graphene.List(lambda: School, required=True)

    @staticmethod
    def resolve_conflicts(parent, info):
        school_names = models.Judge.get_conflicts(parent.tournament_id, parent.id)
        return [School(name=name) for name in school_names]
