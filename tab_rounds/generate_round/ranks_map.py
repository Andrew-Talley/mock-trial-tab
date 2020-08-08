from collections import defaultdict
from itertools import zip_longest, chain

class RanksMap:
  def __init__(self, matchups, round_num):
    super().__init__()
    self.round_num = round_num

    self.ranks = defaultdict(list)
    self.team_category_map = {}

    for matchup in matchups:
      self.team_category_map[matchup['p']] = self.__get_category__('p')
      self.team_category_map[matchup['d']] = self.__get_category__('d')

    self.opponent_map = dict(
      chain(
        ([match['p'], match['d']] for match in matchups),
        ([match['d'], match['p']] for match in matchups),
      )
    )

    def add_to_map(team):
      category = self.team_category_map[team]
      self.ranks[category].append(team)


    if round_num == 2 or round_num == 4:
      for matchup in matchups:
        add_to_map(matchup['p'])
        add_to_map(matchup['d'])
    else:
      for (matchup1, matchup2) in zip_longest(matchups[0::2], matchups[1::2]):
        add_to_map(matchup1['p'])
        add_to_map(matchup1['d'])
        if matchup2 is not None:
          add_to_map(matchup2['d'])
          add_to_map(matchup2['p'])

    self.__rank_map__ = {}
    for rank_list in self.ranks.values():
      for (rank, team) in enumerate(rank_list):
        self.__rank_map__[team] = rank

  def __get_category__(self, side):
    return side if self.round_num % 2 == 0 else "R"

  def __getitem__(self, team):
    return self.rank_for_team(team)

  def rank_for_team(self, team):
    return self.__rank_map__[team]

  def neighbors_for_team(self, team, distance=1):
    category = self.team_category_map[team]
    rank = self.rank_for_team(team)
    neighbors = []

    for offset in [-1, 1]:
      category_ranks = self.ranks[category]
      neighbor_index = rank + offset
      if neighbor_index >= 0 and neighbor_index < len(category_ranks):
        new_neighbor = category_ranks[neighbor_index]
        neighbors.append(new_neighbor)

    neighbors = [n for n in neighbors if self.opponent_map[team]!= n]

    return neighbors
    
  def category_for_team(self, team):
    return self.team_category_map[team]

    