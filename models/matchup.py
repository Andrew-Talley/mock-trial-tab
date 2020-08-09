from models.connection import db, tables

matchup_table = tables['matchup']
ballots_table = tables['ballot']

class Matchup:
  @staticmethod
  def add_matchup(tournament_id, round_num, pl, defense):
    cursor = db.cursor()
    cursor.execute(f"INSERT INTO {matchup_table} (tournament_id, pl_num, def_num, round_num) VALUES (%s, %s, %s, %s)", (tournament_id, pl, defense, round_num))

    db.commit()

    return cursor.lastrowid

  @staticmethod
  def get_matchup(matchup_id):
    cursor = db.cursor()
    cursor.execute(f"SELECT pl_num, def_num, round_num FROM {matchup_table} WHERE id = %s", (matchup_id, ))

    (pl_num, def_num, round_num) = cursor.fetchone()
    return {
      "pl": pl_num,
      "def": def_num,
      "round_num": round_num
    }

  @staticmethod
  def get_ballots(matchup_id: int):
    cursor = db.cursor()
    cursor.execute(f"SELECT id FROM {ballots_table} WHERE matchup_id = %s", (matchup_id, ))

    ballot_ids = [id for (id, ) in cursor.fetchall()]

    return ballot_ids