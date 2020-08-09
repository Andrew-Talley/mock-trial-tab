from models.connection import db, tables

matchup_table = tables['matchup']

class Round:
  @staticmethod
  def get_matchups_for_round(tournament_id, round_num):
    cursor = db.cursor()
    cursor.execute(f"SELECT id, pl_num, def_num FROM {matchup_table} WHERE tournament_id = %s AND round_num = %s", (tournament_id, round_num, ))

    matchups = []
    for id, pl_num, def_num in cursor.fetchall():
      matchups.append({
        "id": id,
        "pl": pl_num,
        "def": def_num
      })

    return matchups