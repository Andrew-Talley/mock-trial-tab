from gql_server.schema import schema
from .test_graphql_server import TestGraphQLServerBase

class TestNotes(TestGraphQLServerBase):
    def test_can_query_speech_notes(self):
        _, _, ballot = self.add_one_matchup_w_judge()
        self.assertSpeechHasNotes(ballot, "PL", "OPENING", None)

    def test_can_assign_speech_notes(self):
        _, _, ballot = self.add_one_matchup_w_judge()

        note = self.assign_speech_notes(ballot, "PL", "OPENING", "Hello, World!")
        self.assertEqual(note, "Hello, World!")
        self.assertSpeechHasNotes(ballot, "PL", "OPENING", "Hello, World!")

    def test_can_reassign_notes(self):
        _, _, ballot = self.add_one_matchup_w_judge()
        self.assign_speech_notes(ballot, "PL", "OPENING", "Hi there!")

        note = self.assign_speech_notes(ballot, "PL", "OPENING", "Howdy there!")
        self.assertEqual(note, "Howdy there!")
        self.assertSpeechHasNotes(ballot, "PL", "OPENING", "Howdy there!")

    def test_can_assign_closing_notes(self):
        _, _, ballot = self.add_one_matchup_w_judge()
        
        note = self.assign_speech_notes(ballot, "DEF", "CLOSING", "Hello, World!")
        self.assertEqual(note, "Hello, World!")
        self.assertSpeechHasNotes(ballot, "DEF", "CLOSING", "Hello, World!")

    def test_can_query_exam_notes(self):
        _, _, ballot = self.add_one_matchup_w_judge()

        self.assertExamHasNotes(None, False, False, 1, "PL", ballot)

    def test_can_set_exam_notes(self):
        _, _, ballot = self.add_one_matchup_w_judge()

        note = self.assign_exam_notes(ballot, "PL", 1, False, False, "Hello, World!")
        self.assertEqual(note, "Hello, World!")
        self.assertExamHasNotes("Hello, World!", False, False, 1, "PL", ballot)

    def test_can_update_exam_notes(self):
        _, _, ballot = self.add_one_matchup_w_judge()
        self.assign_exam_notes(ballot, "PL", 1, False, False, "Hello, World!")

        note = self.assign_exam_notes(ballot, "PL", 1, False, False, "Howdy There!")
        self.assertEqual(note, "Howdy There!")
        self.assertExamHasNotes("Howdy There!", False, False, 1, "PL", ballot)
        
    def test_can_update_all_exam_notes(self):
        _, _, ballot = self.add_one_matchup_w_judge()
        
        note = self.assign_exam_notes(ballot, "DEF", 3, False, True, "Hello everyone")
        self.assertEqual(note, "Hello everyone")
        self.assertExamHasNotes("Hello everyone", True, False, 3, "DEF", ballot)
