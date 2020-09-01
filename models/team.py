from models.connection import db, tables

team_table = tables["team"]
student_table = tables["student"]


class Team:
    @staticmethod
    def create_team(tournament, school, num, name):
        cursor = db.cursor()

        cursor.execute(
            f"INSERT INTO {team_table} (tournament_id, team_num, school_name, name) VALUES (%s, %s, %s, %s)",
            (tournament, num, school, name),
        )

        db.commit()

        return cursor.lastrowid

    # @staticmethod
    # def get_team(tournament_id, num):
    #     cursor = db.cursor()
    #     cursor.execute(
    #         f"SELECT name, school_name FROM {team_table} WHERE tournament_id = %s AND team_num = %s",
    #         (tournament_id, num),
    #     )

    #     (name, school) = cursor.fetchone()

    #     return {"num": num, "name": name, "school": school}

    @staticmethod
    def get_students(tournament_id, num):
        cursor = db.cursor()
        cursor.execute(
            f"SELECT id, student_name FROM {student_table} WHERE tournament_id = %s AND team_num = %s",
            (tournament_id, num),
        )

        students = []
        for (id, name) in cursor.fetchall():
            students.append({"id": id, "name": name})

        return students
