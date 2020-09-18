from models.connection import get_cnx, tables

school_table = tables["school"]
team_table = tables["team"]


class School:
    @staticmethod
    def add_school(tournament_id: int, name: str):
        with get_cnx() as db:
            cursor = db.cursor()
            cursor.execute(
                f"INSERT INTO {school_table} (tournament_id, name) VALUES (%s, %s)",
                (tournament_id, name),
            )

            db.commit()

    @staticmethod
    def get_teams_for_school(tournament_id: int, name: str):
        with get_cnx() as db:
            cursor = db.cursor()
            cursor.execute(
                f"SELECT team_num, name FROM {team_table} WHERE tournament_id = %s AND school_name = %s",
                (tournament_id, name),
            )

            teams = []
            for team_num, name in cursor.fetchall():
                teams.append({"num": team_num, "name": name})

            return teams
