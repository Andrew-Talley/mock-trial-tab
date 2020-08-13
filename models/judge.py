from models.connection import db, tables

judge_table = tables["judge"]
conflict_table = tables["conflict"]
ballots_table = tables["ballot"]


class Judge:
    @staticmethod
    def add_judge(tournament_id: int, name: str):
        cursor = db.cursor()
        cursor.execute(
            f"INSERT INTO {judge_table} (tournament_id, name) VALUES (%s, %s)",
            (tournament_id, name),
        )

        db.commit()

        return cursor.lastrowid

    @staticmethod
    def get_judge(tournament_id: int, id: int):
        cursor = db.cursor()
        cursor.execute(
            f"SELECT tournament_id, id, name FROM {judge_table} WHERE tournament_id = %s AND id = %s",
            (tournament_id, id),
        )

        tourn_id, judge_id, name = cursor.fetchone()

        return {"id": judge_id, "name": name, "tournament_id": tourn_id}

    @staticmethod
    def add_conflict(tournament_id: int, id: int, school: str):
        cursor = db.cursor()
        cursor.execute(
            f"INSERT INTO {conflict_table} (tournament_id, judge_id, school_name) VALUES (%s, %s, %s)",
            (tournament_id, id, school),
        )

        db.commit()

        return cursor.lastrowid

    @staticmethod
    def get_conflicts(tournament_id: int, id: int):
        cursor = db.cursor()
        cursor.execute(
            f"SELECT school_name FROM {conflict_table} WHERE judge_id = %s", (id,)
        )

        conflicts = [name for (name,) in cursor.fetchall()]

        return conflicts

    @staticmethod
    def get_ballots(tournament_id: int, judge_id: int):
        cursor = db.cursor()
        cursor.execute(
            f"SELECT id FROM {ballots_table} WHERE judge_id = %s", (judge_id,)
        )

        ballot_ids = [judge_id for (judge_id,) in cursor.fetchall()]

        return ballot_ids
