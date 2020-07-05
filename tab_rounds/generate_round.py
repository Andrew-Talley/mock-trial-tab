import random
from enum import Enum
from typing import Tuple, List

class Side(Enum):
    PI = 0
    DEF = 1

def __team_ids(sub_teams):
    return [team.get("id") for team in sub_teams]

def separate_pl_and_def_teams(round_num, teams, coin_flip: str) -> Tuple[List[str], List[str]]:
    if (round_num == 2 or round_num == 4):
        p_team_list = [team for team in teams if team["needs_side"] == Side.PI]
        p_teams = __team_ids(p_team_list)

        d_team_list = [team for team in teams if team["needs_side"] == Side.DEF]
        d_teams = __team_ids(d_team_list)
    else:
        left_side = teams[::2]
        right_side = teams[1::2]

        left_ids = __team_ids(left_side)
        right_ids = __team_ids(right_side)

        [p_teams, d_teams] = [left_ids, right_ids] if coin_flip == "Heads" else [right_ids, left_ids]

    return [p_teams, d_teams]

def generate_round(round_num, teams, coin_flip: str):
    teams_copy = teams[:]
    random.shuffle(teams_copy)
    if (round_num > 1):
        teams_copy.sort(
            key=lambda team: team.get("id") if coin_flip == "Heads" else -team.get("id")
        )
    teams_copy.sort(
        key=lambda team: (
            team.get("wins") + team.get("ties") / 2,
            team.get("cs"),
            team.get("pd"),
        )
    )

    [p_teams, d_teams] = separate_pl_and_def_teams(round_num, teams_copy, coin_flip)

    pairings = [{"p": p, "d": d} for (p, d) in zip(p_teams, d_teams)]
    return pairings
