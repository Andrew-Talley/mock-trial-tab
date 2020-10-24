import graphene

import models
from gql_types import Ballot, Judge, Matchup


class AssignJudgeToMatchup(graphene.Mutation):
    class Arguments:
        tournament = graphene.ID(required=True)
        matchup = graphene.ID(required=True)
        judge = graphene.ID(required=True)
        presiding = graphene.Boolean(default_value=False)
        note_only = graphene.Boolean(default_value=False)

    Output = Ballot

    @staticmethod
    def mutate(parent, info, tournament, matchup, judge, presiding, note_only):
        gql_matchup = Matchup(id=matchup)
        gql_judge = Judge(id=judge)

        round_num = Matchup.resolve_round_num(gql_matchup, info)
        if models.Judge.get_ballot_for_round(tournament, judge, round_num) is not None:
            raise Exception(
                f"Judge {judge} already assigned ballot for round {round_num}"
            )

        ballot_id = models.Ballot.create_ballot(matchup, judge, presiding, note_only)
        return Ballot(id=ballot_id, matchup=gql_matchup, judge=gql_judge)
