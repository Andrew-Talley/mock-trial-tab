import graphene

from gql_types import Tournament, School, Team, Judge
from models import (
    Tournament as SQLTournament,
    Team as SQLTeam,
    Judge as SQLJudge,
    School as SQLSchool,
)

from mutations.add_manual_round import AddManualRound
from mutations.assign_judge_to_matchup import AssignJudgeToMatchup
from mutations.add_student_to_team import AddStudentToTeam
from mutations.assign_student_to_role import AssignStudentToRole
from mutations.assign_witness_order import AssignWitnessOrder
from mutations.assign_attorney_to_direct import AssignAttorneyToDirect
from mutations.assign_cross_order import AssignCrossOrder
from mutations.assign_witness_name import AssignWitnessName
from mutations.assign_speech_score import AssignSpeechScore
from mutations.assign_speech_notes import AssignSpeechNotes
from mutations.assign_exam_score import AssignExamScore
from mutations.complete_ballot import CompleteBallot
from mutations.assign_exam_notes import AssignExamNotes


class CreateTournament(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)

    Output = Tournament

    @staticmethod
    def mutate(parent, info, name):
        id = SQLTournament.create_tournament(name)
        tournament_data = SQLTournament.get_all_info_for_tournament(id)

        return Tournament(id=tournament_data["id"], name=tournament_data["name"])


class AddSchool(graphene.Mutation):
    class Arguments:
        tournament = graphene.ID(required=True)
        name = graphene.String(required=True)

    Output = graphene.NonNull(School)

    @staticmethod
    def mutate(parent, info, tournament, name):
        SQLSchool.add_school(tournament, name)
        return School(name=name)


class AddTeam(graphene.Mutation):
    class Arguments:
        tournament = graphene.ID(required=True)
        school = graphene.String(required=True)
        num = graphene.Int(required=True)
        name = graphene.String(required=True)

    Output = Team

    @staticmethod
    def mutate(parent, info, tournament, school, num, name):
        SQLTeam.create_team(tournament, school, num, name)
        return Team(tournament_id=tournament, school_name=school, num=num, name=name)


class AddJudge(graphene.Mutation):
    class Arguments:
        tournament_id = graphene.ID(required=True)
        name = graphene.String(required=True)

    Output = Judge

    @staticmethod
    def mutate(parent, info, tournament_id, name):
        new_id = SQLJudge.add_judge(tournament_id, name)
        return Judge(id=new_id, name=name)


class AddJudgeConflict(graphene.Mutation):
    class Arguments:
        tournament_id = graphene.ID(required=True)
        judge_id = graphene.ID(required=True)
        school = graphene.String(required=True)

    Output = Judge

    @staticmethod
    def mutate(parent, info, tournament_id, judge_id, school):
        SQLJudge.add_conflict(tournament_id, judge_id, school)
        return Judge(id=judge_id, tournament_id=tournament_id)


class Mutation(graphene.ObjectType):
    add_tournament = CreateTournament.Field()

    add_school = AddSchool.Field()
    add_team = AddTeam.Field()

    add_student_to_team = AddStudentToTeam.Field()
    assign_student_to_role = AssignStudentToRole.Field()

    add_manual_round = AddManualRound.Field()

    add_judge = AddJudge.Field(required=True)
    add_judge_conflict = AddJudgeConflict.Field(required=True)
    assign_judge_to_matchup = AssignJudgeToMatchup.Field(required=True)

    assign_witness_order = AssignWitnessOrder.Field(required=True)
    assign_attorney_to_direct = AssignAttorneyToDirect.Field(required=True)
    assign_cross_order = AssignCrossOrder.Field(required=True)
    assign_witness_name = AssignWitnessName.Field(required=True)

    assign_speech_score = AssignSpeechScore.Field(required=True)
    assign_speech_notes = AssignSpeechNotes.Field(required=True)

    assign_exam_score = AssignExamScore.Field(required=True)
    assign_exam_notes = AssignExamNotes.Field(required=True)

    complete_ballot = CompleteBallot.Field(required=True)
