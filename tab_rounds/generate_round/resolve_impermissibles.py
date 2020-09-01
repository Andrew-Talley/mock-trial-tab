from tab_rounds.generate_round.utilities import num_ballots
from tab_rounds.generate_round.ranks_map import RanksMap
from itertools import chain, zip_longest
from collections import defaultdict

class PairSet():
  def __init__(self):
    self.__set__ = set()

  def __serialize_pair__(self, team1, team2):
    [first, second] = sorted([team1, team2], key=lambda team: team['id'])
    return f"{first['id']}-{second['id']}"

  def has(self, team1, team2):
    return self.__serialize_pair__(team1, team2) in self.__set__

  def add(self, team1, team2):
    self.__set__.add(self.__serialize_pair__(team1, team2))

def has_conflict(p, d):
    have_previous_matchups = d['id'] in p['past_pairings']
    same_school = p['school'] == d['school']
    return have_previous_matchups or same_school

def resolve_impermissibles(matchups, team_info, round_num):
  team_map = dict([[team['id'], team] for team in team_info])

  previous_swaps = PairSet()

  def find_conflict():
      for (ind, matchup) in enumerate(matchups):
          p = team_map[matchup['p']]
          d = team_map[matchup['d']]

          if has_conflict(p, d):
              return ind
      
      return None

  def resolve_conflict(row):
      team_matchup_map = dict(chain(
          ([matchup['p'], matchup] for matchup in matchups),
          ([matchup['d'], matchup] for matchup in matchups)
      ))

      ranks_map = RanksMap(matchups, round_num)

      def find_best_option(distance):
        matchup = matchups[row]

        def get_options():
          p, d = matchup['p'], matchup['d']
          p_neighbors = ranks_map.neighbors_for_team(p, distance)
          d_neighbors = ranks_map.neighbors_for_team(d, distance)

          pl_options = [(team_map[p], team_map[neighbor]) for neighbor in p_neighbors]
          def_options = [(team_map[d], team_map[neighbor]) for neighbor in d_neighbors]

          return chain(pl_options, def_options)

        swap_options = get_options()

        swap_options = [
          opt for opt in swap_options if 
            opt is not None and
            not previous_swaps.has(opt[0], opt[1])
        ]

        swap_options.sort(
          key=lambda pair: (
            abs(num_ballots(pair[0]) - num_ballots(pair[1])),
            abs(pair[0]['cs'] - pair[1]['cs']),
            abs(pair[0]['pd'] - pair[1]['pd']),
            -(ranks_map[pair[0]['id']] + ranks_map[pair[1]['id']]),
            ranks_map.category_for_team(pair[0]['id'])
          )
        )


        if len(swap_options) == 0:
          return None

        return swap_options[0]

      def make_swap(team_pair):
        team1, team2 = team_pair
        def find_ind(team):
          match = team_matchup_map[team['id']]
          side = "p" if match["p"] == team['id'] else "d"
          return match, side

        match1, side1 = find_ind(team1)
        match2, side2 = find_ind(team2)

        match1[side1] = team2['id']
        match2[side2] = team1['id']

        previous_swaps.add(team1, team2)

      for distance in range(1, len(matchups) + 1):
        best_option = find_best_option(distance)
        if best_option is not None:
          make_swap(best_option)
          return

  count = 0
  while (conflict_row := find_conflict()) is not None:
    if count > pow(len(matchups), 2):
      raise Exception("Error: Didn't terminate loop")
    resolve_conflict(conflict_row)
    count += 1

  return matchups