from enum import Enum
from typing import List, Any
from itertools import chain
from fractions import Fraction

class Result(Enum):
  WIN = "W"
  TIE = "T"
  LOSS = "L"

def adj_ballots_for_round(elem, iter):
  ballots = list(iter)
  result_count = sum(1 if item == elem else 0 for item in ballots)
  num_ballots = len(ballots)

  if num_ballots == 0:
    return 0

  return Fraction(2 * result_count, num_ballots)

def count_ballots_for_rounds(result: Result, ballots: List[Any]):
  return sum(adj_ballots_for_round(result, r_ballots) for r_ballots in ballots)

def calculate_record(ballots: List[Any]):
  wins = count_ballots_for_rounds(Result.WIN, ballots)
  ties = count_ballots_for_rounds(Result.TIE, ballots)
  losses = count_ballots_for_rounds(Result.LOSS, ballots)

  return {
    "wins": wins,
    "ties": ties,
    "losses": losses
  }