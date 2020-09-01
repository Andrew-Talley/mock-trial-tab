from models.connection import db, tables

student_table = tables["student"]


class Student:
    @staticmethod
    def add_student(tournament_id, team_num, name):
        cursor = db.cursor()
        cursor.execute(
            f"INSERT INTO {student_table} (tournament_id, team_num, student_name) VALUES (%s, %s, %s)",
            (tournament_id, team_num, name),
        )

        db.commit()

        return cursor.lastrowid

    @staticmethod
    def get_student(student_id):
        cursor = db.cursor()
        cursor.execute(
            f"SELECT student_name FROM {student_table} WHERE id = %s", (student_id,)
        )

        return {"name": cursor.fetchone()[0]}
