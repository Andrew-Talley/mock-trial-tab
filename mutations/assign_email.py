import graphene

from gql_types import Judge
import models


class AssignEmail(graphene.Mutation):
    class Arguments:
        tournament = graphene.ID(required=True)
        judge = graphene.ID(required=True)
        email = graphene.String()

    Output = Judge

    @staticmethod
    def mutate(parent, info, tournament, judge, email):
        models.Judge.set_email(judge, email)
        return Judge(id=judge, email=email)
