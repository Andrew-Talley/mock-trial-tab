from models.connection import db, tables

student_table = tables['student']

class Student:
  @staticmethod
  def add_student(tournament_id, team_num, name):
    cursor = db.cursor()
    cursor.execute(f"INSERT INTO {student_table} (tournament_id, team_num, student_name) VALUES (%s, %s, %s)", (tournament_id, team_num, name))

    db.commit()

    return cursor.lastrowid