import random
from typing import Tuple, List
from itertools import zip_longest, chain
from collections import defaultdict
from tab_rounds.generate_round.resolve_impermissibles import resolve_impermissibles
from tab_rounds.generate_round.utilities import Side, get_order_info_for_team

def snake_array(arr):
    def combine_iters(left, right):
        joined = chain.from_iterable(zip_longest(left, right))
        filtered = filter(lambda x: x != None, joined)
        return filtered

    left = combine_iters(arr[0::4], arr[3::4])
    right = combine_iters(arr[1::4], arr[2::4])
    
    return left, right

def __team_ids__(sub_teams):
    return [team.get("id") for team in sub_teams]

def separate_pl_and_def_teams(round_num, teams, coin_flip: str) -> Tuple[List[str], List[str]]:
    if (round_num == 2 or round_num == 4):
        p_team_list = [team for team in teams if team["needs_side"] == Side.PI]
        d_team_list = [team for team in teams if team["needs_side"] == Side.DEF]

        p_teams = __team_ids__(p_team_list)
        d_teams = __team_ids__(d_team_list)
    else:
        left_side, right_side = snake_array(teams)

        left_ids = __team_ids__(left_side)
        right_ids = __team_ids__(right_side)

        (p_teams, d_teams) = (left_ids, right_ids) if coin_flip == "Heads" else (right_ids, left_ids)

    return [p_teams, d_teams]

def generate_round(round_num, teams, coin_flip: str, r3_coin_flip="Heads"):
    teams_copy = teams[:]
    random.shuffle(teams_copy)
    if (round_num > 1):
        teams_copy.sort(
            key=lambda team: -team.get("id") if coin_flip == "Heads" else team.get("id")
        )
        
    teams_copy.sort(
        key=get_order_info_for_team,
        reverse=True
    )

    [p_teams, d_teams] = separate_pl_and_def_teams(round_num, teams_copy, r3_coin_flip)

    pairings = [{"p": p, "d": d} for (p, d) in zip(p_teams, d_teams)]

    pairings = resolve_impermissibles(pairings, teams, round_num)

    return pairings
