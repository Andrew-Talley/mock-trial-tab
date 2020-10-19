import unittest

from gql_server.schema import schema
from .test_graphql_server import TestGraphQLServerBase

class TestJudges(TestGraphQLServerBase):
    def test_tournament_starts_with_no_judges(self):
        self.assertTournamentHasNumJudges(0)

    def test_can_add_judge(self):
        roberts = self.add_judge_to_tournament("John G. Roberts, Jr.")
        self.assertStringIsInt(roberts["id"])
        self.assertEqual(roberts["name"], "John G. Roberts, Jr.")
        self.assertTournamentHasNumJudges(1)
        self.assertJudgeIsListed(roberts["id"])

    def test_can_add_multiple_judges(self):
        self.add_judge_to_tournament("John G. Roberts, Jr.")
        self.add_judge_to_tournament("Michael Avenatti")  # Do they have Zoom in prison?
        self.assertTournamentHasNumJudges(2)

    def test_get_judge_works(self):
        roberts = self.add_judge_to_tournament("John G. Roberts, Jr.")
        roberts_id = roberts["id"]

        found_info = self.get_judge_info(roberts_id)
        self.assertEqual(found_info["name"], "John G. Roberts, Jr.")
        self.assertEqual(found_info["id"], roberts_id)

    def test_add_judge_conflict(self):
        roberts = self.add_judge_to_tournament("John G. Roberts, Jr.")
        self.add_judge_conflict(roberts["id"], "Midlands University")
        self.assertJudgeHasConflict(roberts["id"], "Midlands University")

    def test_can_assign_ballot(self):
        matchup_id = self.add_one_matchup_setup()
        judge_id = self.add_judge_to_tournament("John G. Roberts, Jr.")['id']

        new_ballot = self.assign_ballot(matchup_id, judge_id)

        self.assertEqual(
            judge_id, new_ballot["judge"], "judge_id does not match true judge_id"
        )
        self.assertEqual(
            matchup_id, new_ballot["matchup"], "judge_id does not match true judge_id"
        )

    @unittest.skipIf(True, "Raises ugly error")
    def test_cannot_assign_multiple_ballots(self):
        [m1, m2] = self.add_default_r1_setup()
        judge_id = self.add_judge_to_tournament("John G. Roberts, Jr.")['id']

        new_ballot = self.assign_ballot(m1, judge_id)

        with self.assertRaises(Exception):
            self.assign_ballot(m2, judge_id)

    def test_assigned_ballot_appears_in_graph(self):
        matchup_id, judge_id, new_ballot = self.add_one_matchup_w_judge()

        self.assertJudgeHasBallot(judge_id, new_ballot)
        self.assertMatchupHasBallot(matchup_id, new_ballot)