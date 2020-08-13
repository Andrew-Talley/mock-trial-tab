import graphene

from models import Ballot as SQLBallot
from gql_types import Ballot, Judge, Matchup


class AssignJudgeToMatchup(graphene.Mutation):
    class Arguments:
        matchup = graphene.ID(required=True)
        judge = graphene.ID(required=True)

    Output = Ballot

    @staticmethod
    def mutate(parent, info, matchup, judge):
        ballot_id = SQLBallot.create_ballot(matchup, judge)
        return Ballot(id=ballot_id, matchup=Matchup(id=matchup), judge=Judge(id=judge))
