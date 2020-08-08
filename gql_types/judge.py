import graphene
from models.judge import Judge as SQLJudge
from gql_types.school import School

class Judge(graphene.ObjectType):
  id = graphene.ID(required=True)
  name = graphene.String(required=True)

  tournament_id = graphene.ID(required=True)

  conflicts = graphene.List(lambda: School, required=True)
  @staticmethod
  def resolve_conflicts(parent, info):
    school_names = SQLJudge.get_conflicts(parent.tournament_id, parent.id)
    return [School(name=name) for name in school_names]
