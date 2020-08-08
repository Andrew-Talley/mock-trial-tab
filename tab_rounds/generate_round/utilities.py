from enum import Enum

class Side(Enum):
  PI = 0
  DEF = 1

def num_ballots(team):
  return team['wins'] + team['ties'] / 2

def get_order_info_for_team(team):
  return (
    -1 if team.get("bye_bust") else 1,
    num_ballots(team),
    team.get("cs"),
    team.get("pd")
  )