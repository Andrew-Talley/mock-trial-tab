import unittest
from tab_rounds.generate_round.ranks_map import RanksMap

class RanksMapAssertions:
  def assertTeamHasRank(self, team, rank):
    true_rank = self.ranks_map.rank_for_team(team)
    if true_rank != rank:
      raise AssertionError(f"Expected team {team} to have rank {rank}, but it had a rank of {true_rank} instead")

  def assertTeamHasNeighbor(self, team, neighbor, *, distance=1):
    neighbors = self.ranks_map.neighbors_for_team(team, distance)
    if neighbor not in neighbors:
      raise AssertionError(f"{neighbor} was not found in the neighbors with distance {distance} from {team}. Instead found {neighbors}")

  def assertTeamDoesNotHaveNeighbor(self, team, neighbor, *, distance=1):
    neighbors = self.ranks_map.neighbors_for_team(team, distance)
    if neighbor in neighbors:
      raise AssertionError(f"{team} has neighbor {neighbor} at {distance=}.")


class TestRanksMap(unittest.TestCase, RanksMapAssertions):
  def test_orders_first_teams_in_even_round(self):
    for r_num in [2, 4]:
      with self.subTest(f"Round {r_num}"):
        matchups = [
          {"p": 1, "d": 2}
        ]
        self.ranks_map = RanksMap(matchups, r_num)

        self.assertTeamHasRank(1, 0)
        self.assertTeamHasRank(2, 0)

  def test_orders_all_teams_in_even_round(self):
    for r_num in [2, 4]:
      with self.subTest(f"Round {r_num}"):
        matchups = [
          {"p": i, "d": i+1} for i in range(0, 16, 2)
        ]

        self.ranks_map = RanksMap(matchups, r_num)

        for i in range(0, 16, 2):
          self.assertTeamHasRank(i, i / 2)
          self.assertTeamHasRank(i + 1, i / 2)

  def test_orders_first_teams_in_odd_round(self):
    for r_num in [1, 3]:
      with self.subTest(f"Round {r_num}"):
        matchups = [{"p": 1, "d": 2}]

        self.ranks_map = RanksMap(matchups, r_num)

        self.assertTeamHasRank(1, 0)
        self.assertTeamHasRank(2, 1)

  def test_orders_first_four_teams_in_odd_round(self):
    for r_num in [1, 3]:
      with self.subTest(f"Round {r_num}"):
        matchups = [
          {"p": 0, "d": 1},
          {"p": 3, "d": 2}
        ]

        self.ranks_map = RanksMap(matchups, r_num)

        for i in range(4):
          self.assertTeamHasRank(i, i)

  def test_orders_six_teams_in_odd_round(self):
    for r_num in [1, 3]:
      with self.subTest(f"Round {r_num}"):
        matchups = [
          {"p": 0, "d": 1},
          {"p": 3, "d": 2},
          {"p": 4, "d": 5}
        ]

        self.ranks_map = RanksMap(matchups, r_num)

        for i in range(6):
          self.assertTeamHasRank(i, i)

  def test_finds_adjacent_pl_team(self):
    matchups = [
      {"p": 0, "d": 1},
      {"p": 3, "d": 2},
      {"p": 4, "d": 5}
    ]

    self.ranks_map = RanksMap(matchups, 1)
    self.assertTeamHasNeighbor(3, 4)

  def test_finds_adjacent_def_team(self):
    matchups = [
      {"p": 0, "d": 1},
      {"p": 3, "d": 2}
    ]

    self.ranks_map = RanksMap(matchups, 1)
    self.assertTeamHasNeighbor(1, 2)

  def test_doesnt_return_self_as_neighbor(self):
    matchups = [
      {"p": 0, "d": 1}
    ]

    self.ranks_map = RanksMap(matchups, 1)
    self.assertNotIn(0, self.ranks_map.neighbors_for_team(0))
    self.assertNotIn(1, self.ranks_map.neighbors_for_team(1))

  def test_doesnt_return_opponent_for_odd_round(self):
    matchups = [
      {"p": 0, "d": 1}
    ]

    self.ranks_map = RanksMap(matchups, 1)
    self.assertTeamDoesNotHaveNeighbor(0, 1)
    self.assertTeamDoesNotHaveNeighbor(1, 0)

  def test_doesnt_return_opponent_for_even_round(self):
    matchups = [
      {"p": 0, "d": 1}
    ]

    self.ranks_map = RanksMap(matchups, 2)
    self.assertTeamDoesNotHaveNeighbor(0, 1)
    self.assertTeamDoesNotHaveNeighbor(1, 0)

  def test_finds_neighbor_for_even_round(self):
    matchups = [
      {"p": 0, "d": 1},
      {"p": 2, "d": 3}
    ]

    self.ranks_map = RanksMap(matchups, 2)
    self.assertTeamHasNeighbor(0, 2)
    self.assertTeamHasNeighbor(2, 0)

  def test_finds_neighbors_for_large_odd_round(self):
    matchups = [
      {"p": 0, "d": 1},
      {"p": 3, "d": 2},
      {"p": 4, "d": 5}
    ]

    self.ranks_map = RanksMap(matchups, 3)
    self.assertTeamHasNeighbor(1, 2)
    self.assertTeamHasNeighbor(3, 4)
    self.assertTeamHasNeighbor(4, 3)

    self.assertTeamDoesNotHaveNeighbor(0, 1)
    self.assertTeamDoesNotHaveNeighbor(0, 3)
    self.assertTeamDoesNotHaveNeighbor(0, 2)
    self.assertTeamDoesNotHaveNeighbor(0, 5)

  def test_finds_both_neighbors_for_large_even_round(self):
    matchups = [
      {"p": 0, "d": 4},
      {"p": 1, "d": 5},
      {"p": 2, "d": 6},
      {"p": 3, "d": 7}
    ]

    self.ranks_map = RanksMap(matchups, 2)

    self.assertTeamHasNeighbor(0, 1)
    self.assertTeamHasNeighbor(1, 2)
    self.assertTeamHasNeighbor(2, 3)
    self.assertTeamHasNeighbor(3, 2)
    self.assertTeamHasNeighbor(4, 5)
    self.assertTeamHasNeighbor(5, 6)
    self.assertTeamHasNeighbor(6, 7)

    self.assertTeamDoesNotHaveNeighbor(0, 4)
    self.assertTeamDoesNotHaveNeighbor(0, 5)
    self.assertTeamDoesNotHaveNeighbor(0, 3)

    self.assertTeamDoesNotHaveNeighbor(6, 2)
    self.assertTeamDoesNotHaveNeighbor(6, 3)
