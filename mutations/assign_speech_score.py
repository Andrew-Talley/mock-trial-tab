import graphene

from gql_types import Side, Speech
from models import BallotSections

from .protect_ballot_code import protect_ballot_code


class AssignSpeechScore(graphene.Mutation):
    class Arguments:
        ballot = graphene.ID(required=True)
        side = graphene.Argument(Side, required=True)
        speech = graphene.Argument(Speech, required=True)
        score = graphene.Int(required=True)

    Output = graphene.Int

    @staticmethod
    def mutate(parent, info, ballot, side, speech, score):
        protect_ballot_code(info)
        BallotSections.set_speech_score(ballot, side, speech, score)
        return score
