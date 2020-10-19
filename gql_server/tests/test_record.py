from gql_server.schema import schema
from .test_graphql_server import TestGraphQLServerBase

class TestRecord(TestGraphQLServerBase):
    def test_starts_with_empty_record(self):
        self.create_midlands_a()

        self.assertTeamHasRecord(1001, 0, 0, 0)

    def test_has_two_wins_after_single_ballot_win(self):
        _, judge, ballot = self.add_one_matchup_w_judge()
        self.assign_full_round(ballot, 13)

        self.assertTeamHasRecord(1001, 2, 0, 0)

    def test_has_two_losses_after_single_ballot_loss(self):
        _, judge, ballot = self.add_one_matchup_w_judge()
        self.assign_full_round(ballot, 13)

        self.assertTeamHasRecord(1101, 0, 2, 0)

    def test_yields_ties_for_both_sides(self):
        _, judge, ballot = self.add_one_matchup_w_judge()
        self.assign_full_round(ballot, 0)

        self.assertTeamHasRecord(1001, 0, 0, 2)
        self.assertTeamHasRecord(1101, 0, 0, 2)