from models.connection import db, tables

ballot_table = tables['ballot']

class Ballot:
  @staticmethod
  def create_ballot(matchup_id, judge_id):
    cursor = db.cursor()
    cursor.execute(f"INSERT INTO {ballot_table} (matchup_id, judge_id) VALUES (%s, %s)", (matchup_id, judge_id))

    db.commit()

    return cursor.lastrowid
    