import graphene

from gql_types import Side, Role, ExamType
import models

class AssignExamNotes(graphene.Mutation):
  class Arguments:
    ballot = graphene.ID(required=True)
    side = graphene.Argument(Side, required=True)
    exam = graphene.Int(required=True)
    witness = graphene.Boolean(required=True)
    cross = graphene.Boolean(required=True)
    notes = graphene.String(required=True)

  Output = graphene.String

  @staticmethod
  def mutate(parent, info, ballot, side, exam, witness, cross, notes):
    role = Role.WITNESS if witness else Role.ATTORNEY
    exam_type = ExamType.CROSS if cross else ExamType.DIRECT
    models.BallotSections.set_exam_notes(ballot, side, exam, role, exam_type, notes)
    return notes