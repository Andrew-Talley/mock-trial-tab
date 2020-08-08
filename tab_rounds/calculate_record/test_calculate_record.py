import unittest
from tab_rounds.calculate_record.calculate_record import calculate_record, Result
from fractions import Fraction

class HasRecordAssertion:
  def assertHasRecord(self, record, wins=0, losses=0, ties=0):
    record_wins = record.get('wins')
    if record_wins != wins:
      raise AssertionError(f"Record has {record_wins} wins, not {wins}")

    record_ties = record.get("ties")
    if record_ties != ties:
      raise AssertionError(f"Record has {record_ties} ties, not {ties}")

    record_losses = record.get("losses")
    if record_losses != losses:
      raise AssertionError(f"Record has {record_losses} losses, not {losses}")

class TestCalculateRound(unittest.TestCase, HasRecordAssertion):
  def test_calculate_with_no_ballots(self):
    ballots = []
    record = calculate_record(ballots)

    self.assertHasRecord(record, 0, 0, 0)

  def test_calculates_winful_round(self):
    ballots = [[Result.WIN, Result.WIN]]
    record = calculate_record(ballots)

    self.assertHasRecord(record, wins=2)

  def test_calculates_losing_round(self):
    ballots = [[Result.LOSS, Result.LOSS]]
    record = calculate_record(ballots)

    self.assertHasRecord(record, losses=2)

  def test_calculates_tied_round(self):
    ballots = [[Result.TIE, Result.TIE]]
    record = calculate_record(ballots)

    self.assertHasRecord(record, ties=2)

  def test_calculates_mixed_round(self):
    ballots = [[Result.WIN, Result.LOSS]]
    record = calculate_record(ballots)

    self.assertHasRecord(record, wins=1, losses=1)

  def test_adjusts_for_one_ballot(self):
    ballots = [[Result.WIN]]
    record = calculate_record(ballots)

    self.assertHasRecord(record, wins=2)

  def test_adjusts_for_three_ballots(self):
    ballots = [[Result.WIN, Result.WIN, Result.WIN]]
    record = calculate_record(ballots)

    self.assertHasRecord(record, wins=2)

  def test_adjusts_for_ten_ballots(self):
    ballots = [[Result.WIN for _ in range(10)]]
    record = calculate_record(ballots)

    self.assertHasRecord(record, wins=2)

  def test_returns_fractions_for_three_split_ballots(self):
    ballots = [[Result.WIN, Result.WIN, Result.LOSS]]
    record = calculate_record(ballots)

    self.assertHasRecord(record, wins=Fraction(4, 3), losses=Fraction(2, 3))

  def test_handles_multiple_rounds(self):
    ballots = [[Result.WIN, Result.WIN], [Result.WIN, Result.WIN]]
    record = calculate_record(ballots)

    self.assertHasRecord(record, wins=4)

  def test_handles_multi_round_for_all_results(self):
    ballots = [[Result.WIN, Result.TIE], [Result.WIN, Result.LOSS], [Result.LOSS, Result.LOSS], [Result.WIN, Result.TIE]]
    record = calculate_record(ballots)

    self.assertHasRecord(record, wins=3, ties=2, losses=3)

  def test_permits_varying_ballots_by_round(self):
    ballots = [[Result.WIN, Result.WIN], [Result.WIN, Result.TIE], [Result.LOSS]]
    record = calculate_record(ballots)

    self.assertHasRecord(record, wins=3, ties=1, losses=2)

  def test_handles_multi_round_fractions(self):
    ballots = [[Result.WIN, Result.WIN, Result.TIE], [Result.LOSS, Result.WIN, Result.LOSS], [Result.TIE]]
    record = calculate_record(ballots)

    self.assertHasRecord(record, wins=2, losses=Fraction(4, 3), ties=Fraction(8, 3))

    