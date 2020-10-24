import graphene
from models import Ballot


class DeleteBallot(graphene.Mutation):
    class Arguments:
        ballot = graphene.Argument(graphene.ID, required=True, name="id")

    Output = graphene.Boolean

    @staticmethod
    def mutate(parent, info, ballot):
        return Ballot.delete_ballot(ballot)
