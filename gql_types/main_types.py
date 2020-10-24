from __future__ import annotations
from typing import Tuple, Optional

import graphene
from graphene import NonNull

import models

from gql_types.enums import Role, AttorneyRole, Side, Speech, ExamType
from tab_rounds.calculate_record.calculate_record import calculate_record, Result


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
        if parent.name is not None:
            return parent.name
        return models.Team.get_team(parent.tournament_id, parent.num)["name"]

    num = graphene.Int(required=True)

    school_name = graphene.String(required=True)
    school = NonNull(School)

    tournament_id = graphene.ID(required=True)

    students = NonNull(graphene.List(lambda: Student, required=True))

    matchups = NonNull(graphene.List(lambda: Matchup, required=True))

    @staticmethod
    def resolve_students(parent, info):
        students = models.Team.get_students(parent.tournament_id, parent.num)
        return [Student(id=student["id"], name=student["name"]) for student in students]

    @staticmethod
    def resolve_matchups(parent, info):
        matchup_ids = models.Team.get_matchups(parent.tournament_id, parent.num)
        return [Matchup(id=matchup) for matchup in matchup_ids]

    """
    RECORD INFORMATION
    """
    record: Optional[Tuple[int, int, int]] = None

    @staticmethod
    def get_record(parent, info):
        if parent.record is None:
            matchups = Team.resolve_matchups(parent, info)
            sides = [
                "pl"
                if Matchup.resolve_pl(matchup, info).team_num == parent.num
                else "def"
                for matchup in matchups
            ]
            ballots = [Matchup.resolve_ballots(matchup, info) for matchup in matchups]
            pds = [
                [Ballot.resolve_pd(ballot, info, side) for ballot in round_ballots]
                for round_ballots, side in zip(ballots, sides)
            ]
            results = [
                [
                    Result.WIN if pd > 0 else Result.TIE if pd == 0 else Result.LOSS
                    for pd in round_pds
                    if pd is not None
                ]
                for round_pds in pds
            ]
            parent.record = calculate_record(results)

        return parent.record

    wins = graphene.Int(required=True)

    @staticmethod
    def resolve_wins(parent, info):
        record = Team.get_record(parent, info)
        return record["wins"]

    losses = graphene.Int(required=True)

    @staticmethod
    def resolve_losses(parent, info):
        record = Team.get_record(parent, info)
        return record["losses"]

    ties = graphene.Int(required=True)

    @staticmethod
    def resolve_ties(parent, info):
        record = Team.get_record(parent, info)
        return record["ties"]


class Student(graphene.ObjectType):
    id = graphene.ID(required=True)
    name = graphene.String(required=True)

    @staticmethod
    def resolve_name(parent, info):
        student = models.Student.get_student(parent.id)
        return student["name"]


class BallotSide(graphene.ObjectType):
    side = graphene.Field(Side, required=True)

    _ballot: Ballot = None

    speech = graphene.Int(args={"speech": graphene.Argument(Speech, required=True)})

    @staticmethod
    def get_speech_attr(parent, speech, key):
        speech_data = models.BallotSections.get_speech_section(
            parent._ballot.id, parent.side, speech
        )
        if speech_data is None:
            return None
        return speech_data[key]

    @staticmethod
    def get_exam_attr(parent, info, order, role, exam_type, attr):
        exam = models.BallotSections.get_exam_section(
            parent._ballot.id, parent.side, order, role, exam_type
        )
        if exam is None:
            return None
        return exam[attr]

    @staticmethod
    def resolve_speech(parent, info, speech):
        return BallotSide.get_speech_attr(parent, speech, "score")

    speech_notes = graphene.String(
        args={"speech": graphene.Argument(Speech, required=True)}
    )

    @staticmethod
    def resolve_speech_notes(parent, info, speech):
        return BallotSide.get_speech_attr(parent, speech, "notes")

    exam = graphene.Int(
        args={
            "order": graphene.Int(required=True),
            "role": graphene.Argument(Role, required=True),
            "exam_type": graphene.Argument(ExamType, required=True, name="type"),
        },
    )

    @staticmethod
    def resolve_exam(parent, info, order, role, exam_type):
        return BallotSide.get_exam_attr(parent, info, order, role, exam_type, "score")

    exam_notes = graphene.String(
        args={
            "order": graphene.Int(required=True),
            "role": graphene.Argument(Role, required=True),
            "exam_type": graphene.Argument(ExamType, required=True, name="type"),
        },
    )

    @staticmethod
    def resolve_exam_notes(parent, info, order, role, exam_type):
        return BallotSide.get_exam_attr(parent, info, order, role, exam_type, "notes")

    side_sum = graphene.Int(required=True, name="sum")

    @staticmethod
    def resolve_side_sum(parent, info):
        return models.BallotSections.get_sum(parent._ballot.id, parent.side)


class Ballot(graphene.ObjectType):
    id = graphene.ID(required=True)
    matchup = graphene.Field(lambda: Matchup, required=True)
    judge = graphene.Field(lambda: Judge, required=True)

    side = graphene.Field(
        BallotSide, args={"side": graphene.Argument(Side, required=True)}, required=True
    )

    pd = graphene.Int(args={"side": graphene.Argument(Side, required=True)})

    witness_awards = graphene.List(lambda: MatchupWitness, required=True)

    attorney_awards = graphene.List(lambda: MatchupAttorney, required=True)

    complete = graphene.Boolean(required=True)

    @staticmethod
    def resolve_side(parent, info, side):
        ballot_side = BallotSide(side=side)
        ballot_side._ballot = parent
        return ballot_side

    @staticmethod
    def resolve_pd(parent, info, side):
        pl_sum = models.BallotSections.get_sum(parent.id, Side.PL)
        def_sum = models.BallotSections.get_sum(parent.id, Side.DEF)

        if pl_sum is None or def_sum is None:
            return None

        pl_pd = pl_sum - def_sum

        if side == Side.PL:
            return pl_pd
        else:
            return -pl_pd

    @staticmethod
    def resolve_complete(parent, info):
        return models.Ballot.get_is_complete(parent.id)

    @staticmethod
    def resolve_judge(parent, info):
        return Judge(models.Ballot.get_judge_for_ballot(parent.id))

    @staticmethod
    def resolve_matchup(parent, info):
        return Matchup(id=models.Ballot.get_matchup_for_ballot(parent.id))

    @staticmethod
    def get_individual_awards(parent, info, witness):
        return [
            models.Ballot.get_rank_for_ballot(parent.id, witness, rank)
            for rank in range(1, 5)
        ]

    @staticmethod
    def resolve_witness_awards(parent, info):
        ranks = Ballot.get_individual_awards(parent, info, True)
        return [
            None if s_id is None else MatchupWitness(student_id=s_id) for s_id in ranks
        ]

    @staticmethod
    def resolve_attorney_awards(parent, info):
        ranks = Ballot.get_individual_awards(parent, info, False)
        return [
            None if s_id is None else MatchupAttorney(student=Student(id=s_id))
            for s_id in ranks
        ]


class MatchupWitness(graphene.ObjectType):
    matchup_team = graphene.Field(lambda: MatchupTeam, required=True)
    order = graphene.Int()
    student = graphene.Field(Student)
    student_id = graphene.ID(required=True)
    witness_name = graphene.String()

    @staticmethod
    def resolve_student(parent, info):
        if parent.student_id:
            return Student(id=parent.student_id)

        student_id = models.Examination.get_witness_in_order(
            parent.matchup_team.matchup_id, parent.matchup_team.side, parent.order
        )
        if student_id is None:
            return None
        else:
            return Student(id=student_id)

    @staticmethod
    def resolve_witness_name(parent, info):
        return models.Examination.get_witness_name(
            parent.matchup_team.matchup_id, parent.matchup_team.side, parent.order
        )


class MatchupAttorney(graphene.ObjectType):
    student = graphene.Field(Student)


class MatchupTeam(graphene.ObjectType):
    tournament_id = graphene.ID(required=True)
    matchup_id = graphene.ID(required=True)
    team_num = graphene.Int(required=True)
    side = graphene.Field(Side, required=True)

    team = graphene.Field(Team, required=True)

    @staticmethod
    def resolve_team(parent, info):
        return Team(num=parent.team_num, tournament_id=parent.tournament_id)

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
            if student_id is None:
                return None

            return MatchupAttorney(student=Student(id=student_id))

        order = kwargs.get("order", None)
        if order is not None:
            attorney_id = models.Examination.get_attorney_in_order(
                parent.matchup_id, parent.side, order
            )
            if attorney_id is None:
                return None

            return MatchupAttorney(student=Student(id=attorney_id))

        crossing_wit = kwargs.get("crossing_witness_num")
        if crossing_wit is not None:
            attorney_id = models.Examination.get_attorney_crossing_witness(
                parent.matchup_id, parent.side, crossing_wit
            )
            if attorney_id is None:
                return None

            return MatchupAttorney(student=Student(id=attorney_id))


class Matchup(graphene.ObjectType):
    id = graphene.ID(required=True)

    pl = graphene.Field(MatchupTeam, required=True)
    defense = graphene.Field(MatchupTeam, required=True, name="def")

    @staticmethod
    def resolve_pl(parent, info):
        return Matchup.resolve_team(parent, info, "pl")

    @staticmethod
    def resolve_defense(parent, info):
        return Matchup.resolve_team(parent, info, "def")

    round_num = graphene.Int(required=True)

    @staticmethod
    def resolve_round_num(parent, info):
        match = models.Matchup.get_matchup(parent.id)
        return match["round_num"]

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

    notes = graphene.String()

    @staticmethod
    def resolve_notes(parent, info):
        new_notes = models.Matchup.get_notes(parent.id)
        return new_notes


class Judge(graphene.ObjectType):
    id = graphene.ID(required=True)
    name = graphene.String(required=True)

    tournament_id = graphene.ID(required=True)

    ballots = graphene.List(Ballot, required=True)

    @staticmethod
    def resolve_name(parent, info):
        return models.Judge.get_judge(parent.tournament_id, parent.id)["name"]

    @staticmethod
    def resolve_ballots(parent, info):
        ballot_ids = models.Judge.get_ballots(parent.tournament_id, parent.id)
        return [Ballot(id=id) for id in ballot_ids]

    conflicts = graphene.List(lambda: School, required=True)

    @staticmethod
    def resolve_conflicts(parent, info):
        school_names = models.Judge.get_conflicts(parent.tournament_id, parent.id)
        return [School(name=name) for name in school_names]

    email = graphene.String()

    @staticmethod
    def resolve_email(parent, info):
        return models.Judge.get_email(parent.id)
