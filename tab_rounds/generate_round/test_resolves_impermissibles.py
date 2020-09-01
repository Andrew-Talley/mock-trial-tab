import unittest
from tab_rounds.generate_round.test_generate_round import get_team, InSameRoundAssertion
from tab_rounds.generate_round.resolve_impermissibles import resolve_impermissibles
from tab_rounds.generate_round.utilities import Side

class TestResolvesImpermissibles(unittest.TestCase, InSameRoundAssertion):
  def test_doesnt_pair_teams_twice(self):
    teams = [
      get_team(1, past_pairings=[2]),
      get_team(2, past_pairings=[1]),
      get_team(3, past_pairings=[4]),
      get_team(4, past_pairings=[3])
    ]

    matchups = [
      {"p": 1, "d": 2},
      {"p": 4, "d": 3}
    ]
    self.pairings = resolve_impermissibles(matchups, teams, 1)

    self.assertPairingExists(1, 3, enforce_sides=True)
    self.assertPairingExists(4, 2, enforce_sides=True)

  def test_finds_deeper_impermissible(self):
    teams = [
      get_team(1),
      get_team(2),
      get_team(3),
      get_team(4),
      get_team(5, past_pairings=[6]),
      get_team(6, past_pairings=[5]),
      get_team(7),
      get_team(8)
    ]

    matchups = [
      {"p": 1, "d": 2},
      {"p": 4, "d": 3},
      {"p": 5, "d": 6},
      {"p": 8, "d": 7},
    ]
    self.pairings = resolve_impermissibles(matchups, teams, 1)

    self.assertPairingExists(5, 7, True)
    self.assertPairingExists(8, 6, True)

  def test_forbids_same_school_matchup(self):
      teams = [
          get_team(1, school=1),
          get_team(2, school=1),
          get_team(3),
          get_team(4)
      ]

      matchups = [
        {"p": 1, "d": 2},
        {"p": 4, "d": 3}
      ]
      self.pairings = resolve_impermissibles(matchups, teams, 1)

      self.assertPairingExists(1, 3)
      self.assertPairingExists(2, 4)

  def test_switches_same_side_for_r2(self):
      teams = [
          get_team(1),
          get_team(2, past_pairings=[5]),
          get_team(3),
          get_team(4),
          get_team(5, past_pairings=[2]),
          get_team(6)
      ]

      matchups = [
        {"p": 1, "d": 4},
        {"p": 2, "d": 5},
        {"p": 3, "d": 6}
      ]
      self.pairings = resolve_impermissibles(matchups, teams, 2)

      self.assertPairingExists(2, 6, enforce_sides=True)
      self.assertPairingExists(3, 5, enforce_sides=True)
  
  def test_prefers_small_ballot_diff(self):
      teams = [
          get_team(1, wins=2, side=Side.PI),
          get_team(2, wins=1, side=Side.PI, past_pairings=[5]),
          get_team(3, wins=0, side=Side.PI),
          get_team(4, wins=1, ties=1, side=Side.DEF),
          get_team(5, wins=1, side=Side.DEF, past_pairings=[2]),
          get_team(6, side=Side.DEF)
      ]

      matchups = [
        {"p": 1, "d": 4},
        {"p": 2, "d": 5},
        {"p": 3, "d": 6}
      ]
      self.pairings = resolve_impermissibles(matchups, teams, 2)

      self.assertPairingExists(1, 5, enforce_sides=True)
      self.assertPairingExists(2, 4, enforce_sides=True)

  def test_prefers_small_cs_diff(self):
    teams = [
        get_team(1, cs=4, side=Side.PI),
        get_team(2, cs=2, side=Side.PI, past_pairings=[5]),
        get_team(3, side=Side.PI),
        get_team(4, cs=3, side=Side.DEF),
        get_team(5, cs=2, side=Side.DEF, past_pairings=[2]),
        get_team(6, side=Side.DEF)
    ]

    matchups = [
      {"p": 1, "d": 4},
      {"p": 2, "d": 5},
      {"p": 3, "d": 6}
    ]
    self.pairings = resolve_impermissibles(matchups, teams, 2)

    self.assertPairingExists(1, 5, enforce_sides=True)
    self.assertPairingExists(2, 4, enforce_sides=True)

  def test_prefers_small_pd_diff(self):
    teams = [
      get_team(1, pd=4, side=Side.PI),
      get_team(2, side=Side.PI, past_pairings=[5]),
      get_team(3, pd=-3, side=Side.PI),
      get_team(4, pd=1, side=Side.DEF),
      get_team(5, side=Side.DEF, past_pairings=[2]),
      get_team(6, pd=-2, side=Side.DEF)
    ]

    matchups = [
      {"p": 1, "d": 4},
      {"p": 2, "d": 5},
      {"p": 3, "d": 6}
    ]
    self.pairings = resolve_impermissibles(matchups, teams, 2)

    self.assertPairingExists(1, 5, enforce_sides=True)
    self.assertPairingExists(2, 4, enforce_sides=True)

  def test_prefers_larger_rank_sum(self):
    with self.subTest("6 teams"):
      teams = [
        get_team(1),
        get_team(2),
        get_team(3, school=10),
        get_team(4, school=10),
        get_team(5),
        get_team(6)
      ]

      # Should swap 4 and 5
      matchups = [
        {"p": 1, "d": 2},
        {"p": 4, "d": 3},
        {"p": 5, "d": 6},
      ]
      self.pairings = resolve_impermissibles(matchups, teams, 3)

      self.assertPairingExists(5, 3, enforce_sides=True)
      self.assertPairingExists(4, 6, enforce_sides=True)

    with self.subTest("8 teams"):
      teams = [
        get_team(i) for i in range(1, 9)
      ]
      teams[4]['school'] = 13 # Team 5
      teams[5]['school'] = 13 # Team 6

      matchups = [
        {"p": 1, "d": 2},
        {"p": 4, "d": 3},
        {"p": 5, "d": 6},
        {"p": 8, "d": 7},
      ]
      self.pairings = resolve_impermissibles(matchups, teams, 2)

      self.assertPairingExists(5, 7, enforce_sides=True)
      self.assertPairingExists(8, 6, enforce_sides=True)

  def test_doesnt_repeat_swap(self):
    teams = [
      get_team(1),
      get_team(2),
      get_team(3, school=10),
      get_team(4, school=10),
      get_team(5, school=10),
      get_team(6)
    ]

    # Should swap 4 and 5, then 2 and 3
    matchups = [
      {"p": 1, "d": 2},
      {"p": 4, "d": 3},
      {"p": 5, "d": 6},
    ]
    self.pairings = resolve_impermissibles(matchups, teams, 3)

    self.assertPairingExists(1, 3, enforce_sides=True)
    self.assertPairingExists(5, 2, enforce_sides=True)
    self.assertPairingExists(4, 6, enforce_sides=True)

  def test_prefers_swapping_def(self):
    """
      Original grid:
      1 ≠ 4
      2   5
      3 ≠ 6

      If P swaps, this becomes
      2   4
      1   5
      3 ≠ 6

      Then, 5 and 6 swap, and 3 is matched against 5.

      If D is swapped, it becomes
      1   5
      2   4
      3 ≠ 6

      Then, 4 and 6 are swapped, and 3 is matched against 4
    """
    teams = [
      get_team(1, wins=1, school=10),
      get_team(2, wins=1, past_pairings=[4]),
      get_team(3, school=19),
      get_team(4, wins=1, school=10, past_pairings=[2]),
      get_team(5, wins=1),
      get_team(6, wins=1, school=19),
    ]

    matchups = [
      {"p": 1, "d": 4},
      {"p": 2, "d": 5},
      {"p": 3, "d": 6},
    ]

    self.pairings = resolve_impermissibles(matchups, teams, 2)
    self.assertPairingExists(3, 4)

  def test_looks_beyond_adjacent_neighbors_when_necessary(self):
    teams = [
      get_team(1, past_pairings=[5]),
      get_team(2, school=12, past_pairings=[4]),
      get_team(3),
      get_team(4, past_pairings=[2]),
      get_team(5, school=12, past_pairings=[1]),
      get_team(6),
    ]

    # Should switch 4/5, then 1/2, then 5/6
    matchups = [
      {"p": 1, "d": 4},
      {"p": 2, "d": 5},
      {"p": 3, "d": 6},
    ]
    self.pairings = resolve_impermissibles(matchups, teams, 2)

    self.assertPairingExists(2, 6, enforce_sides=True)
    self.assertPairingExists(1, 4, enforce_sides=True)
    self.assertPairingExists(3, 5, enforce_sides=True)

  def test_throws_error_on_impossible_pairing(self):
    teams = [
      get_team(1, past_pairings=[2], wins=2),
      get_team(2, past_pairings=[1])
    ]
    matchups = [{"p": 1, "d": 2}]

    with self.assertRaises(Exception):
      resolve_impermissibles(matchups, teams, 2)

if __name__ == "__main__":
    unittest.main()
