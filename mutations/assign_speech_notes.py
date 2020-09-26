import graphene

from gql_types import Side, Speech
import models


class AssignSpeechNotes(graphene.Mutation):
    class Arguments:
        ballot = graphene.ID(required=True)
        side = graphene.Argument(Side, required=True)
        speech = graphene.Argument(Speech, required=True)
        notes = graphene.String(required=True)

    Output = graphene.String

    @staticmethod
    def mutate(parent, info, ballot, side, speech, notes):
        models.BallotSections.set_speech_notes(ballot, side, speech, notes)
        return notes
