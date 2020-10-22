from .test_graphql_server import TestGraphQLServerBase
from gql_server.schema import schema

class IndividualAwardsBase(TestGraphQLServerBase):
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

class TestIndividualAwards(IndividualAwardsBase):
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

class TestIndividualAwardResults(IndividualAwardsBase):
  def get_outstanding_competitors(self, role):
    result = schema.execute(
      f"""
        query getIndividualAwards {{
          tournament(id: {self.tourn_id}) {{
            outstandingCompetitors(role: {role}) {{
              side
              ranks
              student {{
                id
              }}
            }}
          }}
        }}
      """
    )

    witnesses = result.data['tournament']['outstandingCompetitors']
    return witnesses

  def test_starts_without_witnesses(self):
    witnesses = self.get_outstanding_competitors("WITNESS")
    self.assertEqual(type(witnesses), list)
    self.assertEqual(len(witnesses), 0)

  def test_sums_individual_awards(self):
    _, _, ballot = self.add_one_matchup_w_judge()
    bayes_id = self.add_elizabeth_bayes()
    self.assign_individual_award(ballot, "WITNESS", bayes_id)

    witnesses = self.get_outstanding_competitors("WITNESS")
    self.assertEqual(len(witnesses), 1)

    [bayes_award] = witnesses
    self.assertEqual(bayes_award['side'], "PL")
    self.assertEqual(bayes_award['ranks'], 10)
    self.assertEqual(bayes_award['student']['id'], bayes_id)

  def test_sums_attorney_awards(self):
    _, _, ballot = self.add_one_matchup_w_judge()
    bayes_id = self.add_elizabeth_bayes()
    self.assign_individual_award(ballot, "ATTORNEY", bayes_id)

    attorneys = self.get_outstanding_competitors("ATTORNEY")
    self.assertEqual(len(attorneys), 1)

    [bayes_award] = attorneys
    self.assertEqual(bayes_award['side'], "PL")
    self.assertEqual(bayes_award['ranks'], 10)
    self.assertEqual(bayes_award['student']['id'], bayes_id)

  def test_sums_all_ranks(self):
    _, _, ballot = self.add_one_matchup_w_judge()
    bayes_id = self.add_elizabeth_bayes()
    self.assign_individual_award(ballot, "WITNESS", bayes_id, rank=2)

    [award] = self.get_outstanding_competitors("WITNESS")
    self.assertEqual(award['ranks'], 8)

  def test_averages_awards_by_number_of_ballots(self):
    match, _, ballot = self.add_one_matchup_w_judge()
    bayes_id = self.add_elizabeth_bayes()
    next_judge = self.add_judge_to_tournament("Michael Avenatti")
    next_ballot = self.assign_ballot(match, next_judge['id'])

    self.assign_individual_award(ballot, "WITNESS", bayes_id)
    self.assign_individual_award(next_ballot['id'], "WITNESS", bayes_id)
    [award] = self.get_outstanding_competitors("WITNESS")
    self.assertEqual(award['ranks'], 10)

  def test_orders_by_number_of_ranks(self):
    _, _, ballot = self.add_one_matchup_w_judge()

    students = [self.add_student_to_team(1001, f"Student f{n}")['student']['id'] for n in range(1, 4)]

    for number, student in enumerate(reversed(students)):
      self.assign_individual_award(ballot, "WITNESS", student, 1 + number)

    award_winners = self.get_outstanding_competitors("WITNESS")

    for winner, expectedRank in zip(award_winners, range(10, 4, -2)):
      self.assertEqual(winner['ranks'], expectedRank)
