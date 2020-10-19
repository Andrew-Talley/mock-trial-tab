from gql_server.schema import schema
from .test_graphql_server import TestGraphQLServerBase

class TestScoring(TestGraphQLServerBase):
    def test_can_score_and_modify_opening(self):
        _, judge, ballot = self.add_one_matchup_w_judge()

        score = self.assign_speech_score(ballot, "PL", "OPENING", 10)
        self.assertEqual(score, 10)
        self.assertSpeechHasScore(10, "OPENING", "PL", ballot)

        score = self.assign_speech_score(ballot, "PL", "OPENING", 8)
        self.assertEqual(score, 8)
        self.assertSpeechHasScore(8, "OPENING", "PL", ballot)

    def test_can_score_and_modify_closing(self):
        _, judge, ballot = self.add_one_matchup_w_judge()

        self.assign_speech_score(ballot, "PL", "CLOSING", 10)
        self.assertSpeechHasScore(10, "CLOSING", "PL", ballot)

        self.assign_speech_score(ballot, "PL", "CLOSING", 8)
        self.assertSpeechHasScore(8, "CLOSING", "PL", ballot)

    def test_can_score_atty_direct(self):
        _, judge, ballot = self.add_one_matchup_w_judge()

        score = self.assign_exam_score(ballot, "PL", 1, False, False, 8)

        self.assertEqual(score, 8)
        self.assertExamHasScore(8, False, False, 1, "PL", ballot)

        self.assign_exam_score(ballot, "PL", 1, False, False, 10)
        self.assertExamHasScore(10, False, False, 1, "PL", ballot)

    def test_can_score_atty_cross(self):
        _, judge, ballot = self.add_one_matchup_w_judge()

        score = self.assign_exam_score(ballot, "PL", 1, False, True, 8)
        self.assertExamHasScore(8, True, False, 1, "PL", ballot)

    def test_can_sum_scores(self):
        _, judge, ballot = self.add_one_matchup_w_judge()

        self.assign_exam_score(ballot, "PL", 1, False, False, 10)
        self.assertBallotSideHasSum(ballot, "PL", 10)

    def test_sum_updates(self):
        _, judge, ballot = self.add_one_matchup_w_judge()

        self.assign_exam_score(ballot, "PL", 1, False, False, 10)
        self.assertBallotSideHasSum(ballot, "PL", 10)

        self.assign_exam_score(ballot, "PL", 1, False, False, 8)
        self.assertBallotSideHasSum(ballot, "PL", 8)

    def test_can_sum_speeches(self):
        _, judge, ballot = self.add_one_matchup_w_judge()

        self.assign_speech_score(ballot, "PL", "OPENING", 10)
        self.assertBallotSideHasSum(ballot, "PL", 10)

    def test_can_sum_exams_and_speeches(self):
        _, judge, ballot = self.add_one_matchup_w_judge()

        self.assign_speech_score(ballot, "PL", "OPENING", 6)
        self.assign_exam_score(ballot, "PL", 1, False, False, 9)
        self.assertBallotSideHasSum(ballot, "PL", 15)

    def test_sums_sides_independently(self):
        _, judge, ballot = self.add_one_matchup_w_judge()

        self.assign_speech_score(ballot, "PL", "OPENING", 8)
        self.assign_speech_score(ballot, "DEF", "OPENING", 9)

        self.assertBallotSideHasSum(ballot, "PL", 8)
        self.assertBallotSideHasSum(ballot, "DEF", 9)

    def test_finds_pd(self):
        _, judge, ballot = self.add_one_matchup_w_judge()

        self.assign_speech_score(ballot, "PL", "OPENING", 8)
        self.assign_speech_score(ballot, "DEF", "OPENING", 9)

        self.assertBallotHasPD(ballot, "PL", -1)

    def test_full_round_scoring(self):
        _, judge, ballot = self.add_one_matchup_w_judge()

        self.assign_full_round(ballot, 13)

        self.assertBallotHasPD(ballot, "PL", 13)

    def test_starts_uncompleted(self):
        _, _, ballot = self.add_one_matchup_w_judge()

        self.assertBallotIsDone(ballot, False)

    def test_can_complete_round_after_score(self):
        _, _, ballot = self.add_one_matchup_w_judge()
        self.assign_full_round(ballot, 13)

        self.assertBallotIsDone(ballot, False)
        
        result = schema.execute(f"""
            mutation completeBallot {{
                completeBallot(tournament: {self.tourn_id}, ballot: {ballot}) {{
                    complete
                }}
            }}
        """)


        self.assertTrue(result.data['completeBallot']['complete'])

        self.assertBallotIsDone(ballot)
