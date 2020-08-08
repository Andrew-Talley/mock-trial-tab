from models.connection import db, tables

matchup_table = tables['matchup']

class Matchup:
  @staticmethod
  def add_matchup(tournament_id, round_num, pl, defense):
    cursor = db.cursor()
    cursor.execute(f"INSERT INTO {matchup_table} (tournament_id, pl_num, def_num, round_num) VALUES (%s, %s, %s, %s)", (tournament_id, pl, defense, round_num))

    db.commit()

    return cursor.lastrowid