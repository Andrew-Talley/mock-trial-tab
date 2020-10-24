import graphene
from gql_types import Ballot
import models


class NoteOnlyBallot(graphene.Mutation):
    class Arguments:
        ballot = graphene.ID(required=True, name="id")
        note_only = graphene.Boolean(default_value=True)

    Output = Ballot

    @staticmethod
    def mutate(parent, info, ballot, note_only):
        models.Ballot.set_score_only(ballot, note_only)
        return Ballot(id=ballot)
