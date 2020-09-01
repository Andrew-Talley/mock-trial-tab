import graphene

from gql_types import Matchup, Side
from models import Examination


class AssignWitnessName(graphene.Mutation):
    class Arguments:
        tournament = graphene.ID(required=True)
        matchup = graphene.ID(required=True)
        side = graphene.Argument(Side, required=True)
        order = graphene.Int(required=True)
        witness = graphene.String(required=True)

    matchup = graphene.Field(Matchup, required=True)
    witness_name = graphene.String(required=True)

    @staticmethod
    def mutate(parent, info, tournament, matchup, side, order, witness):
        Examination.assign_witness_name(matchup, side, order, witness)
        new_matchup = Matchup(id=matchup)
        return AssignWitnessName(matchup=new_matchup, witness_name=witness)
