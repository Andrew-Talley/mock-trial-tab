import graphene

from gql_types import Side, Role, ExamType
from models import BallotSections

from .protect_ballot_code import protect_ballot_code


class AssignExamScore(graphene.Mutation):
    class Arguments:
        ballot = graphene.ID(required=True)
        side = graphene.Argument(Side, required=True)

        exam = graphene.Int(required=True)
        witness = graphene.Boolean(required=True)
        cross = graphene.Boolean(required=True)

        score = graphene.Int(required=True)

    Output = graphene.Int

    @staticmethod
    def mutate(parent, info, ballot, side, exam, witness, cross, score):
        protect_ballot_code(info)
        role = Role.WITNESS if witness else Role.ATTORNEY
        exam_type = ExamType.CROSS if cross else ExamType.DIRECT
        exam_score = BallotSections.set_exam_score(
            ballot, side, exam, role, exam_type, score
        )
        return exam_score["score"]
