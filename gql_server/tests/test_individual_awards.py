from .test_graphql_server import TestGraphQLServerBase
from gql_server.schema import schema

class TestIndividualAwards(TestGraphQLServerBase):
  def get_attorney_awards(self, ballot):
    result = schema.execute(f"""
      query getWitnessAward {{
        tournament(id: {self.tourn_id}) {{
          ballot(id: {ballot}) {{
            attorneyAwards {{
              student {{
                id
              }}
            }}
          }}
        }}
      }}
    """)

    awards = result.data['tournament']['ballot']['attorneyAwards']

    return awards

  def get_witness_awards(self, ballot):
    result = schema.execute(f"""
      query getWitnessAward {{
        tournament(id: {self.tourn_id}) {{
          ballot(id: {ballot}) {{
            witnessAwards {{
              # witnessName
              student {{
                id
                name
              }}
            }}
          }}
        }}
      }}
    """)

    awards = result.data['tournament']['ballot']["witnessAwards"]

    return awards

  def assign_individual_award(self, ballot, role, student, rank=1):
    result = schema.execute(f"""
      mutation assignWitnessAward {{
        assignIndividualAward(ballot: {ballot}, role: {role}, student: {student}, rank: {rank}) {{
          rank
          role {{
            ... on MatchupWitness {{
              student {{
                id
              }}
            }}
            ... on MatchupAttorney {{
              student {{
                id
              }}
            }}
          }}
        }}
      }}
    """)

    return result.data['assignIndividualAward']

  def assertStudentHasRank(self, student, rank, ballot, *, witness=True):
    awards = self.get_witness_awards(ballot) if witness else self.get_attorney_awards(ballot)
    rank_holder = awards[rank - 1]
    self.assertIsNotNone(rank_holder)
    self.assertEqual(rank_holder['student']['id'], student)

  def test_can_query_unfilled_witness(self):
    _, judge, ballot = self.add_one_matchup_w_judge()
    self.get_witness_awards(ballot)

  def test_can_query_unfilled_attorney(self):
    _, judge, ballot = self.add_one_matchup_w_judge()
    self.get_attorney_awards(ballot)

  def test_witness_starts_with_empty_list_of_len_4(self):
    _, judge, ballot = self.add_one_matchup_w_judge()
    awards = self.get_witness_awards(ballot)

    self.assertEqual(type(awards), list)
    self.assertEqual(len(awards), 4)

  def test_attorney_starts_with_empty_list_of_len_4(self):
    _, judge, ballot = self.add_one_matchup_w_judge()
    awards = self.get_witness_awards(ballot)

    self.assertEqual(type(awards), list)
    self.assertEqual(len(awards), 4)

  def test_can_assign_witness_award(self):
    _, _, ballot = self.add_one_matchup_w_judge()
    bayes_id = self.add_elizabeth_bayes()
    
    assignment = self.assign_individual_award(ballot, "WITNESS", bayes_id)
    self.assertEqual(assignment['rank'], 1)
    student = assignment['role']['student']
    self.assertEqual(student['id'], bayes_id)
    self.assertStudentHasRank(bayes_id, 1, ballot)

  def test_can_reassign_witness_award(self):
    _, _, ballot = self.add_one_matchup_w_judge()
    neibart = self.add_student_to_team(1001, "Elias Neibart")['student']['id']
    sonali = self.add_student_to_team(1001, "Sonali Mehta")['student']['id']

    self.assign_individual_award(ballot, "WITNESS", neibart)
    self.assertStudentHasRank(neibart, 1, ballot)

    self.assign_individual_award(ballot, "WITNESS", sonali)
    self.assertStudentHasRank(sonali, 1, ballot)

  def test_can_assign_attorney_award(self):
    _, _, ballot = self.add_one_matchup_w_judge()
    bayes_id = self.add_elizabeth_bayes()
    
    assignment = self.assign_individual_award(ballot, "ATTORNEY", bayes_id)
    self.assertEqual(assignment['rank'], 1)
    student = assignment['role']['student']
    self.assertEqual(student['id'], bayes_id)
    self.assertStudentHasRank(bayes_id, 1, ballot, witness=False)

  def test_can_assign_all_scores(self):
    _, _, ballot = self.add_one_matchup_w_judge()
    witnesses = [self.add_student_to_team(1001, f"Witness {i}")['student']['id'] for i in range(1, 5)]
    attorneys = [self.add_student_to_team(1101, f"Attorney {i}")['student']['id'] for i in range(1, 5)]

    for rank, (witness, attorney) in enumerate(zip(witnesses, attorneys)):
      self.assign_individual_award(ballot, "WITNESS", witness, rank + 1)
      self.assign_individual_award(ballot, "ATTORNEY", attorney, rank + 1)

    for rank, (witness, attorney) in enumerate(zip(witnesses, attorneys)):
      self.assertStudentHasRank(witness, rank + 1, ballot, witness=True)
      self.assertStudentHasRank(attorney, rank + 1, ballot, witness=False)
