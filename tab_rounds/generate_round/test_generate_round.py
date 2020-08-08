import unittest
from fractions import Fraction
from tab_rounds.generate_round.generate_round import generate_round
from tab_rounds.generate_round.utilities import Side

school_id = 1

def get_team(id, wins=0, ties=0, losses=0, cs=0, ocs=0, pd=0, side=None, bye_bust=False, school=None, past_pairings=[]):
    global school_id 
    school_id += 1

    school_value = school_id if school == None else school

    return {
        "id": id,
        "wins": wins,
        "ties": ties,
        "losses": losses,
        "cs": cs,
        "ocs": ocs,
        "pd": pd,
        "needs_side": side,
        "bye_bust": bye_bust,
        "school": school_value,
        "past_pairings": past_pairings
    }


class InSameRoundAssertion:
    pairings = []

    def assertPairingExists(self, p, d, enforce_sides=False):
        if not any(r["p"] == p and r["d"] == d for r in self.pairings):
            if enforce_sides:
                raise AssertionError(f"No round with π {p} and ∆ {d}")
            elif not any(r["d"] == p and r["p"] == d for r in self.pairings):
                raise AssertionError(f"No round with {p} and {d}")

    def assertTeamInRound(self, team, round):
        if round["p"] != team and round["d"] != team:
            raise AssertionError(f"Team {team} not in round {round}")


class TestGenerateRound(unittest.TestCase, InSameRoundAssertion):
    def serialize_pairings(self, pairings):
        joined_pairs = [str(r["p"]) + str(r["d"]) for r in pairings]
        output_str = "".join(joined_pairs)
        return output_str

    def sort_pairings_by_team_id(self, pairings):
        pairings.sort(key=lambda pair: min(pair["p"], pair["d"]))

    def test_pairs_teams(self):
        teams = [get_team(1), get_team(2)]

        self.pairings = generate_round(1, teams, "Heads")

        self.assertPairingExists(1, 2)

    def test_randomly_pairs_empty_teams(self):
        teams = [get_team(x, 0, 0, 0, 0, 0) for x in range(100)]

        pairings_1 = generate_round(1, teams, "Heads")
        pairings_2 = generate_round(1, teams, "Heads")

        serialized_1 = self.serialize_pairings(pairings_1)
        serialized_2 = self.serialize_pairings(pairings_2)

        # Chance these aren't equal < 1/10^156
        self.assertNotEqual(serialized_1, serialized_2)

    def test_pairs_high_high(self):
        # Teams from 1 - 8, where team 01 has 4 losses, team 2 has 3 losses and a tie, team 3 with 3 losses and a win, etc. (#/2 ballots)
        teams = [
            get_team(x, wins=x // 2, ties=x % 2, losses=(4 - x // 2 - x % 2))
            for x in range(8)
        ]

        self.pairings = generate_round(1, teams, "Heads")

        for (team_1, team_2) in zip(range(0, 8, 2), range(1, 8, 2)):
            with self.subTest(teams=(team_1, team_2)):
                self.assertPairingExists(team_1, team_2)

    def test_always_pairs_bye_bust_last(self):
        teams = [
            get_team(1, wins=1, losses=1),
            get_team(2, wins=1, losses=1),
            get_team(3, losses=2),
            get_team(4, wins=2, bye_bust=True)
        ]

        self.pairings = generate_round(1, teams, "Heads")

        self.assertPairingExists(1, 2)
        self.assertPairingExists(3, 4)
                
    def test_handles_fractions(self):
        teams = [
            get_team(0, wins=2),
            get_team(1, wins=Fraction(4, 3), losses=Fraction(2, 3)),
            get_team(2, wins=Fraction(2, 3), losses=Fraction(4, 2)),
            get_team(3, losses=2)
        ]

        self.pairings = generate_round(1, teams, "Heads")

        self.assertPairingExists(0, 1)
        self.assertPairingExists(2, 3)

    def test_accounts_for_ties(self):
        teams = [
            get_team(0, wins=4),
            get_team(1, wins=1, ties=3),
            get_team(2, wins=2, losses=2),
            get_team(3, losses=4),
        ]

        self.pairings = generate_round(1, teams, "Heads")

        self.assertPairingExists(0, 1)

    def test_uses_cs_tie_breaker(self):
        teams = [
            get_team(0, wins=4), get_team(1, wins=2, cs=16),
        ]
        teams.extend(get_team(team_num, wins=2, cs=8) for team_num in range(2, 50))

        self.pairings = generate_round(1, teams, "Heads")
        self.assertPairingExists(0, 1)

    def test_uses_pd_tie_breaker(self):
        teams = [get_team(0, wins=4)]
        teams.extend(get_team(team_num, wins=2, pd=8) for team_num in range(2, 50))
        teams.append(get_team(1, wins=2, pd=16))

        self.pairings = generate_round(1, teams, "Heads")
        self.assertPairingExists(0, 1)

    def test_coin_flip_determines_sides(self):
        teams = [
            get_team(8 - team_num, wins=team_num // 2, ties=team_num % 2)
            for team_num in range(0, 8)
        ]

        self.pairings = generate_round(3, teams, "Tails", "Tails")

        self.assertPairingExists(2, 1, True)
        self.assertPairingExists(3, 4, True)

        self.pairings = generate_round(3, teams, "Heads", "Heads")

        self.assertPairingExists(1, 2, True)
        self.assertPairingExists(4, 3, True)

    def test_coin_flip_determines_rank(self):
        teams = [
            get_team(1, wins=4),
            get_team(2, wins=2),
            get_team(3, wins=2),
            get_team(4, wins=0),
        ]

        with self.subTest("Heads"):
            for i in range(10): # Ensure it is deterministic
                self.pairings = generate_round(3, teams, "Heads")
                self.assertPairingExists(1, 3)
                self.assertPairingExists(2, 4)

        with self.subTest("Tails"):
            for i in range(10):
                self.pairings = generate_round(3, teams, "Tails")
                self.assertPairingExists(1, 2)
                self.assertPairingExists(3, 4)


    def test_pairs_pl_and_def(self):
        teams = [
            get_team(0, wins=1, side=Side.PI),
            get_team(1, wins=1, side=Side.PI),
            get_team(2, losses=1, side=Side.DEF),
            get_team(3, losses=1, side=Side.DEF)
        ]

        for i in range(10):
            self.pairings = generate_round(2, teams, "Heads")

            self.assertPairingExists(0, 2, True)
            self.assertPairingExists(1, 3, True)

    def test_snakes_teams_in_round_3(self):
        teams = [
            get_team(0, wins=4),
            get_team(1, wins=2, ties=1, losses=1),
            get_team(2, wins=1, ties=1, losses=2),
            get_team(3, losses=4)
        ]

        self.pairings = generate_round(3, teams, "Heads")

        self.assertPairingExists(0, 1, True)
        self.assertPairingExists(3, 2, True)

    def test_snakes_r1_as_pl_in_r3(self):
        teams = [
            get_team(0, wins=4),
            get_team(1, wins=3),
            get_team(2, wins=2, ties=1),
            get_team(3, wins=1, ties=1),
            get_team(4, wins=1),
            get_team(5)
        ]

        self.pairings = generate_round(3, teams, "Heads")

        self.assertPairingExists(0, 1, True)
        self.assertPairingExists(3, 2, True)
        self.assertPairingExists(4, 5, True)

    def test_calls_resolve_impermissibles(self):
        teams = [
            get_team(1, wins=2, past_pairings=[2]),
            get_team(2, wins=1, ties=1, past_pairings=[1]),
            get_team(3, losses=1, ties=1, past_pairings=[4]),
            get_team(4, losses=2, past_pairings=[3])
        ]

        self.pairings = generate_round(3, teams, "Heads")

        self.assertPairingExists(1, 3)
        self.assertPairingExists(4, 2)

    def test_real_rounds(self):
        for true_round in true_rounds:
            with self.subTest(true_round['name']):
                self.pairings = generate_round(true_round['round'], true_round['teams'], true_round['coin_flip'], true_round['r3_coin_flip'])

                for [p, d] in true_round["true_pairs"]:
                    self.assertPairingExists(p, d, enforce_sides=True)





true_rounds = [
    # {
    #     "name": "Uhh...",
    #     "round": 2,
    #     "coin_flip": "Heads",
    #     "teams": [
    #         get_team(1006, losses=2, pd=-17, side=Side.DEF),
    #         get_team(1007, wins=1, ties=1, pd=13, side=Side.DEF),
    #         get_team(1052, wins=1, losses=1, pd=-2, side=Side.DEF),
    #         get_team(1053, wins=1, losses=1, pd=2, side=Side.DEF),
    #         get_team(1154, wins=1, losses=1, pd=14, side=Side.DEF),
    #         get_team(1155, wins=2, pd=13, side=Side.PI),
    #         get_team(1181, wins=2, pd=17, side=Side.PI),
    #         get_team(1184, wins=2, pd=13, side=Side.DEF),
    #         get_team(1195, wins=2, pd=8, side=Side.DEF),
    #         get_team(1196, wins=2, pd=19, side=Side.DEF),
    #         get_team(1206, wins=1, losses=1, pd=-8, side=Side.DEF),
    #         get_team(1302, ties=1, losses=1, pd=-13, side=Side.PI),
    #         get_team(1303, losses=2, pd=-20, side=Side.DEF),
    #         get_team(1376, losses=2, pd=-8, side=Side.PI),
    #         get_team(1377, losses=2, pd=-13, side=Side.DEF),
    #         get_team(1381, losses=2, pd=-13, side=Side.PI),
    #         get_team(1389, wins=1, losses=1, pd=2, side=Side.PI),
    #         get_team(1390, losses=2, pd=-46, side=Side.DEF),
    #         get_team(1410, wins=1, losses=1, pd=-14, side=Side.PI),
    #         get_team(1507, wins=1, losses=1, pd=8, side=Side.PI),
    #         get_team(1508, wins=2, pd=46, side=Side.PI),
    #         get_team(1555, losses=2, pd=-19, side=Side.PI),
    #         get_team(1652, wins=1, losses=1, pd=-2, side=Side.PI),
    #         get_team(1653, wins=2, pd=20, side=Side.PI)
    #     ],
    #     "true_pairs": [
    #         [1376, 1006],
    #         [1155, 1007],
    #         [1652, 1052],
    #         [1389, 1053],
    #         [1507, 1154],
    #         [1181, 1195],
    #         [1653, 1184],
    #         [1508, 1196],
    #         [1410, 1206],
    #         [1302, 1377],
    #         [1381, 1303],
    #         [1555, 1390],
    #     ]
    # },
    {
        "name": "Scarlett and Grey, 2019",
        "round": 3,
        "coin_flip": "Heads",
        "r3_coin_flip": "Heads", # Flipped from actual, but they seem to have still said Left=prosecution
        "teams": [
            get_team(1000, wins=1, ties=1, losses=2, cs=2, pd=-28, school="Michigan", past_pairings=[1302, 1381]),
            get_team(1001, losses=4, cs=4, pd=-36, past_pairings=[1010, 1113], school="Miami"),
            get_team(1002, wins=3, losses=1, cs=4, pd=41, school="Miami", past_pairings=[1143, 1610]),
            get_team(1010, wins=2, losses=2, cs=3, pd=6, school="Macalaster", past_pairings=[1001, 1182]),
            get_team(1040, wins=2, losses=2, cs=3, pd=-25, school="Loyola", past_pairings=[1243, 1609]),
            get_team(1113, wins=2, losses=2, cs=3, pd=7, school="Notre Dame", past_pairings=[1389, 1001]),
            get_team(1114, wins=3, losses=1, cs=3, pd=59, school="Notre Dame", past_pairings=[1609, 1243]),
            get_team(1143, wins=1, losses=3, cs=4, pd=-24, school="Dayton", past_pairings=[1002, 1311]),
            get_team(1182, wins=3, ties=1, cs=2.5, pd=27, school="Ohio State", past_pairings=[1362, 1010]),
            get_team(1183, wins=3, losses=1, cs=4, pd=62, school="Ohio State", past_pairings=[1310, 1535]),
            get_team(1195, wins=4, pd=55, cs=1.5, school="UT Chatt", past_pairings=[1381, 1302]),
            get_team(1243, wins=3, losses=1, cs=5, pd=29, school="Hamilton", past_pairings=[1040, 1114]),
            get_team(1302, wins=2, losses=2, cs=5.5, pd=28, school="Duke", past_pairings=[1000, 1195]),
            get_team(1310, wins=1, losses=3, cs=4, pd=-30, school="Ohio", past_pairings=[1183, 1330]),
            get_team(1311, wins=1, losses=3, cs=4, pd=-36, school="Ohio", past_pairings=[1610, 1143]),
            get_team(1330, wins=1, losses=3, cs=4, pd=-19, school="Duquesne", past_pairings=[1535, 1310]),
            get_team(1362, ties=1, losses=3, cs=5.5, pd=-34, school="Case Western", past_pairings=[1182, 1560]),
            get_team(1381, ties=1, losses=3, cs=5.5, pd=-55, school="Vanderbilt", past_pairings=[1195, 1000]),
            get_team(1389, wins=3, losses=1, cs=5, pd=12, school="Indiana", past_pairings=[1113, 1593]),
            get_team(1534, wins=4, pd=64, cs=2, school="Cincinnatti", past_pairings=[1870, 1652]),
            get_team(1535, wins=3, losses=1, cs=4, pd=-13, school="Cincinnati", past_pairings=[1330, 1183]),
            get_team(1560, wins=2, losses=2, cs=3.5, pd=1, school="PSU", past_pairings=[1593, 1362]),
            get_team(1592, wins=2, losses=2, cs=2, pd=-15, school="Michigan State", past_pairings=[1652, 1870]),
            get_team(1593, wins=3, losses=1, cs=5, pd=27, school="Michigan State", past_pairings=[1560, 1389]),
            get_team(1609, losses=4, pd=-53, cs=5, school="Northwestern", past_pairings=[1114, 1040]),
            get_team(1610, wins=3, losses=1, cs=4, pd=19, school="Northwestern", past_pairings=[1311, 1002]),
            get_team(1652, wins=2, losses=2, cs=6, pd=25, school="UGA", past_pairings=[1592, 1534]),
            get_team(1870, losses=4, pd=-74, cs=6, school="Bye Bust", bye_bust=True, past_pairings=[1534, 1592])
        ],
        "true_pairs": [
            [1002, 1183], 
            [1010, 1113], 
            [1040, 1592], 
            [1143, 1310], 
            [1243, 1389], 
            [1302, 1560], 
            [1330, 1000], 
            [1362, 1311], 
            [1381, 1609], 
            [1534, 1195], 
            [1593, 1182], 
            [1610, 1535], 
            [1652, 1114], 
            [1870, 1001]
            ]
    }
]

