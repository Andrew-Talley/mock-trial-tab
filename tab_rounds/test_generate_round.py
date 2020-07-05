import unittest
from tab_rounds.generate_round import generate_round, Side

def get_team(id, wins=0, ties=0, losses=0, cs=0, ocs=0, pd=0, side=None):
    return {
        "id": id,
        "wins": wins,
        "ties": ties,
        "losses": losses,
        "cs": cs,
        "ocs": ocs,
        "pd": pd,
        "needs_side": side,
    }


class InSameRoundAssertion:
    def assertPairingExists(self, p, d, round, enforce_sides=False):
        if not any(r["p"] == p and r["d"] == d for r in round):
            if enforce_sides:
                raise AssertionError(f"No round with π {p} and ∆ {d}")
            elif not any(r["d"] == p and r["p"] == d for r in round):
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
        teams = [get_team(1, 0, 0, 0, 0, 0), get_team(2, 0, 0, 0, 0, 0)]

        pairings = generate_round(1, teams, "Heads")
        self.assertPairingExists(1, 2, pairings)

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

        pairings = generate_round(1, teams, "Heads")

        for (team_1, team_2) in zip(range(0, 8, 2), range(1, 8, 2)):
            with self.subTest(teams=(team_1, team_2)):
                self.assertPairingExists(team_1, team_2, pairings)

    def test_accounts_for_ties(self):
        teams = [
            get_team(0, wins=4),
            get_team(1, wins=1, ties=3),
            get_team(2, wins=2, losses=2),
            get_team(3, losses=4),
        ]

        pairings = generate_round(1, teams, "Heads")

        self.assertPairingExists(0, 1, pairings)

    def test_uses_cs_tie_breaker(self):
        teams = [get_team(0, wins=4), get_team(1, wins=2, cs=16)]
        teams.extend(get_team(team_num, wins=2, cs=8) for team_num in range(2, 50))

        pairings = generate_round(1, teams, "Heads")

        self.assertPairingExists(0, 1, pairings)

    def test_uses_pd_tie_breaker(self):
        teams = [get_team(0, wins=4)]
        teams.extend(get_team(team_num, wins=2, pd=8) for team_num in range(2, 50))
        teams.append(get_team(1, wins=2, pd=16))

        pairings = generate_round(1, teams, "Heads")

        self.assertPairingExists(0, 1, pairings)

    def test_coin_flip_determines_size(self):
        teams = [
            get_team(8 - team_num, wins=team_num // 2, ties=team_num % 2)
            for team_num in range(0, 8)
        ]

        pairings = generate_round(3, teams, "Tails")

        for team_num in range(1, 9, 2):
            with self.subTest(team_nums=(team_num, team_num + 1), side="Tails"):
                self.assertPairingExists(
                    team_num, team_num + 1, pairings, enforce_sides=True
                )

        pairings = generate_round(3, teams, "Heads")

        for team_num in range(1, 9, 2):
            with self.subTest(team_nums=(team_num, team_num + 1), side="Heads"):
                self.assertPairingExists(
                    team_num + 1, team_num, pairings, enforce_sides=True
                )

    def test_coin_flip_determines_rank(self):
        teams = [
            get_team(1, wins=4),
            get_team(2, wins=2),
            get_team(3, wins=2),
            get_team(4, wins=0),
        ]

        with self.subTest("Heads"):
            for i in range(10): # Ensure it is deterministic
                pairings = generate_round(3, teams, "Heads")
                self.assertPairingExists(1, 3, pairings)
                self.assertPairingExists(2, 4, pairings)

        with self.subTest("Tails"):
            for i in range(10):
                pairings = generate_round(3, teams, "Tails")
                self.assertPairingExists(1, 2, pairings)
                self.assertPairingExists(3, 4, pairings)


    def test_pairs_pl_and_def(self):
        teams = [
            get_team(0, wins=1, side=Side.PI),
            get_team(1, wins=1, side=Side.PI),
            get_team(2, losses=1, side=Side.DEF),
            get_team(3, losses=1, side=Side.DEF)
        ]

        for i in range(10):
            pairings = generate_round(2, teams, "Heads")

            self.assertPairingExists(0, 2, pairings, enforce_sides=True)
            self.assertPairingExists(1, 3, pairings, enforce_sides=True)

    def test_complex_round_2(self):
        teams = [
            get_team(1006, losses=2, pd=-17, side=Side.DEF),
            get_team(1007, wins=1, ties=1, pd=13, side=Side.DEF),
            get_team(1052, wins=1, losses=1, pd=-2, side=Side.DEF),
            get_team(1053, wins=1, losses=1, pd=2, side=Side.DEF),
            get_team(1154, wins=1, losses=1, pd=14, side=Side.DEF),
            get_team(1155, wins=2, pd=13, side=Side.PI),
            get_team(1181, wins=2, pd=17, side=Side.PI),
            get_team(1184, wins=2, pd=13, side=Side.DEF),
            get_team(1195, wins=2, pd=8, side=Side.DEF),
            get_team(1196, wins=2, pd=19, side=Side.DEF),
            get_team(1206, wins=1, losses=1, pd=-8, side=Side.DEF),
            get_team(1302, ties=1, losses=1, pd=-13, side=Side.PI),
            get_team(1303, losses=2, pd=-20, side=Side.DEF),
            get_team(1376, losses=2, pd=-8, side=Side.PI),
            get_team(1377, losses=2, pd=-13, side=Side.DEF),
            get_team(1381, losses=2, pd=-13, side=Side.PI),
            get_team(1389, wins=1, losses=1, pd=2, side=Side.PI),
            get_team(1390, losses=2, pd=-46, side=Side.DEF),
            get_team(1410, wins=1, losses=1, pd=-14, side=Side.PI),
            get_team(1507, wins=1, losses=1, pd=8, side=Side.PI),
            get_team(1508, wins=2, pd=46, side=Side.PI),
            get_team(1555, losses=2, pd=-19, side=Side.PI),
            get_team(1652, wins=1, losses=1, pd=-2, side=Side.PI),
            get_team(1653, wins=2, pd=20, side=Side.PI)
        ]

        pairings = generate_round(2, teams, "Heads")

        true_pairs = [
            [1376, 1006],
            [1155, 1007],
            [1652, 1052],
            [1389, 1053],
            [1507, 1154],
            [1181, 1195],
            [1653, 1184],
            [1508, 1196],
            [1410, 1206],
            [1302, 1377],
            [1381, 1303],
            [1555, 1390],
        ]

        for [p, d] in true_pairs:
            self.assertPairingExists(p, d, pairings, enforce_sides=True)

    


if __name__ == "__main__":
    unittest.main()
