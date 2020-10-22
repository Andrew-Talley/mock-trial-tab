from gql_server.schema import schema
from .test_graphql_server import TestGraphQLServerBase

class TestMatchups(TestGraphQLServerBase):
    def get_matchup_notes(self, matchup):
        result = schema.execute(
            f"""
                query getMatchupNotes {{
                    tournament(id: {self.tourn_id}) {{
                        matchup(id: {matchup}) {{
                            notes
                        }}
                    }}
                }}
            """
        )

        notes = result.data['tournament']['matchup']['notes']
        return notes

    def assign_notes(self, matchup, notes):
        result = schema.execute(
            f"""
                mutation setMatchupNotes {{
                    assignMatchupNotes(tournament: {self.tourn_id}, matchup: {matchup}, notes: "{notes}") {{
                        matchup {{
                            id
                        }}
                        notes
                    }}
                }}
            """
        )

        result = result.data['assignMatchupNotes']

        return result

    def test_starts_with_no_rounds(self):
        self.assertHasNumRounds(0)

    def test_can_add_manual_round(self):
        self.add_default_team_matrix()
        matchups = self.add_round(
            1, [{"pl": 1001, "def": 1101}, {"pl": 1002, "def": 1102}]
        )
        self.assertHasNumRounds(1)
        self.assertHasRound(1)
        self.assertHasMatchup(matchups[0], 1001, 1101)
        self.assertHasMatchup(matchups[1], 1002, 1102)

    def test_team_has_matchup(self):
        [matchup, _] = self.add_default_r1_setup()
        result = schema.execute(
            f"""
            query teamMatchups {{
                tournament(id: {self.tourn_id}) {{
                    team(num: {1001}) {{
                        matchups {{
                            id
                        }}
                    }}
                }}
            }}
            """
        )

        [gql_matchup] = result.data['tournament']['team']['matchups']

        self.assertEqual(matchup, gql_matchup['id'])

    def test_matchup_gives_round_num(self):
        [matchup, _] = self.add_default_r1_setup()
        result = schema.execute(
            f"""
            query teamMatchups {{
                tournament(id: {self.tourn_id}) {{
                    matchup(id: {matchup}) {{
                        roundNum
                    }}
                }}
            }}
            """
        )

        round_num = result.data['tournament']['matchup']['roundNum']

        self.assertEqual(round_num, 1)

    def test_matchup_teams_are_fully_explorable(self):
        matchup = self.add_one_matchup_setup()
        result = schema.execute(
            f"""
            query teamMatchups {{
                tournament(id: {self.tourn_id}) {{
                    matchup(id: {matchup}) {{
                        pl {{
                            team {{
                                num
                                name
                            }}
                        }}
                        def {{
                            team {{
                                num
                                name
                            }}
                        }}
                    }}
                }}
            }}
            """
        )

        match = result.data['tournament']['matchup']
        pl = match['pl']['team']
        self.assertEqual(pl['num'], 1001)
        self.assertEqual(pl['name'], "Midlands University A")

        de = match['def']['team']
        self.assertEqual(de['num'], 1101)
        self.assertEqual(de['name'], "Midlands State University A")

    def test_matchup_starts_with_no_notes(self):
        matchup = self.add_one_matchup_setup()
        notes = self.get_matchup_notes(matchup)
        self.assertIsNone(notes)

    def test_can_assign_notes(self):
        matchup = self.add_one_matchup_setup()
        result = self.assign_notes(matchup, "Hello, World!")
        self.assertEqual(result['matchup']['id'], matchup)
        self.assertEqual(result['notes'], "Hello, World!")

        notes = self.get_matchup_notes(matchup)
        self.assertEqual(notes, "Hello, World!")

    def test_can_reassign_notes(self):
        matchup = self.add_one_matchup_setup()
        self.assign_notes(matchup, "Hey there!")
        self.assign_notes(matchup, "Hey there Delilah")
        self.assertEqual(self.get_matchup_notes(matchup), "Hey there Delilah")
