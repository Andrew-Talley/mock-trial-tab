import graphene

from gql_types import Role, MatchupWitness, MatchupAttorney, Student
from models import Ballot


class IndividualAwardRole(graphene.Union):
    class Meta:
        types = (MatchupAttorney, MatchupWitness)


class AssignIndividualAward(graphene.Mutation):
    class Arguments:
        ballot = graphene.ID(required=True)
        role = graphene.Argument(Role, required=True)
        student = graphene.ID(required=True)
        rank = graphene.Int(required=True)

    rank = graphene.Int(required=True)
    role = graphene.Field(IndividualAwardRole, required=True)

    @staticmethod
    def mutate(parent, info, ballot, role, student, rank):
        # passed_code = info.context.headers.get("Ballot-Code")
        # true_code = os.environ.get("code")

        # if passed_code != true_code:
        #     raise Exception("User not authorized to modify ballot")

        is_witness = role == Role.WITNESS
        Ballot.set_rank_for_ballot(ballot, is_witness, rank, student)

        role = (
            MatchupWitness(student_id=student)
            if is_witness
            else MatchupAttorney(student=Student(id=student))
        )
        return AssignIndividualAward(rank=1, role=role)
