from models.connection import db, tables

team_table = tables['team']

class Team:
  @staticmethod
  def create_team(tournament, school, num, name):
    cursor = db.cursor()

    cursor.execute(f"INSERT INTO {team_table} (tournament_id, team_num, school_name, name) VALUES (%s, %s, %s, %s)", (tournament, num, school, name))

    db.commit()
