from models.connection import db, tables

tournament_table = tables['tournament']
school_table = tables['school']
team_table = tables['team']
judge_table = tables['judge']
matchup_table = tables['matchup']

class Tournament:
  @staticmethod
  def create_tournament(name):
    cursor = db.cursor()
    cursor.execute(f"INSERT INTO {tournament_table} (name) VALUES (%s)", (name, ))

    db.commit()

    return cursor.lastrowid

  @staticmethod
  def get_all_tournaments():
    cursor = db.cursor()
    cursor.execute(f"SELECT * FROM {tournament_table}")

    tournaments = []
    for (id, name) in cursor.fetchall():
      tournaments.append({"id": id, "name": name})

    return tournaments

  @staticmethod
  def get_all_info_for_tournament(id):
    cursor = db.cursor()
    cursor.execute(f"SELECT * FROM {tournament_table} WHERE tournament_id = %s", (id, ))

    (id, name) = cursor.fetchone()

    return {"id": id, "name": name}

  @staticmethod
  def get_schools_for_tournament(tournament_id: int):
    cursor = db.cursor()
    cursor.execute(f"SELECT * FROM {school_table} WHERE tournament_id = %s", (tournament_id, ))

    schools = []
    for tourn_id, name in cursor.fetchall():
      schools.append({
        "tournament_id": tourn_id,
        "name": name
      })

    return schools

  @staticmethod
  def get_teams_for_tournament(tournament_id: int):
    cursor = db.cursor()
    cursor.execute(f"SELECT * FROM {team_table} WHERE tournament_id = %s", (tournament_id, ))

    teams = []
    for tourn_id, team_num, school_name, team_name in cursor.fetchall():
      teams.append({
        "tournament_id": tourn_id,
        "num": team_num,
        "name": team_name,
        "school_name": school_name
      })

    return teams

  @staticmethod
  def get_judges_for_tournament(tournament_id: int):
    cursor = db.cursor()
    cursor.execute(f"SELECT * FROM {judge_table} WHERE tournament_id = %s", (tournament_id, ))

    teams = []
    for tournament_id, judge_id, name in cursor.fetchall():
      teams.append({
        "tournament_id": tournament_id,
        "id": judge_id,
        "name": name,
      })

    return teams

  @staticmethod
  def get_all_rounds(tournament_id: int):
    cursor = db.cursor()
    cursor.execute(f"SELECT DISTINCT round_num FROM {matchup_table} WHERE tournament_id = %s", (tournament_id, ))

    rounds = [num for (num, ) in cursor.fetchall()]
    
    return rounds
    
  @staticmethod
  def delete_tournament(id):
    cursor = db.cursor()
    cursor.execute(f"DELETE FROM {tournament_table} WHERE tournament_id = %s", (id, ))

    db.commit()

    return True
