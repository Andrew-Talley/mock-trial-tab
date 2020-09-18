import graphene

import models
from gql_types import Ballot


class CompleteBallot(graphene.Mutation):
    class Arguments:
        tournament = graphene.ID(required=True)
        ballot = graphene.ID(required=True)

    Output = Ballot

    @staticmethod
    def mutate(parent, info, tournament, ballot):
        models.Ballot.set_is_complete(ballot, True)
        return Ballot(id=ballot)
