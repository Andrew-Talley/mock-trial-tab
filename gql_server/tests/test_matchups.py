from gql_server.schema import schema
from .test_graphql_server import TestGraphQLServerBase

class TestMatchups(TestGraphQLServerBase):
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
        [matchup, _] = self.add_default_r1_setup()
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
