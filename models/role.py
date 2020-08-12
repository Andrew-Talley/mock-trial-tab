from models.connection import db, tables

role_table = tables['role']

class Role:
  @staticmethod
  def assign_role(tournament_id, matchup_id, team_num, student_id, role):
    cursor = db.cursor()
    cursor.execute(f"INSERT INTO {role_table} (tournament_id, matchup_id, team_num, student_id, role) VALUES (%s, %s, %s, %s, %s)", (tournament_id, matchup_id, team_num, student_id, role))

    db.commit()

    return cursor.lastrowid

  @staticmethod
  def get_student_in_role(tournament_id, matchup_id, team_num, role):
    cursor = db.cursor()
    cursor.execute(f"SELECT student_id FROM {role_table} WHERE tournament_id = %s AND matchup_id = %s AND team_num = %s AND role = %s", (tournament_id, matchup_id, team_num, role))

    (student_id, ) = cursor.fetchone()

    return student_id