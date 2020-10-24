import graphene

from gql_types import Matchup
import models


class AssignMatchupNotes(graphene.Mutation):
    class Arguments:
        tournament = graphene.ID(required=True)
        matchup = graphene.ID(required=True)
        notes = graphene.String(required=True)

    matchup = graphene.Field(Matchup, required=True)
    notes = graphene.String(required=True)

    @staticmethod
    def mutate(parent, info, tournament, matchup, notes):
        models.Matchup.set_notes(matchup, notes)
        return {"matchup": Matchup(id=matchup), "notes": notes}
