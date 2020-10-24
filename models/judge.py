from models.connection import get_cnx, tables

judge_table = tables["judge"]
conflict_table = tables["conflict"]
ballots_table = tables["ballot"]
ballot_matchup_table = tables["ballot_matchup_info"]


class Judge:
    @staticmethod
    def add_judge(tournament_id: int, name: str):
        with get_cnx() as db:
            cursor = db.cursor()
            cursor.execute(
                f"INSERT INTO {judge_table} (tournament_id, name) VALUES (%s, %s)",
                (tournament_id, name),
            )

            db.commit()

            return cursor.lastrowid

    @staticmethod
    def get_judge(tournament_id: int, id: int):
        with get_cnx() as db:
            cursor = db.cursor()
            cursor.execute(
                f"SELECT tournament_id, id, name FROM {judge_table} WHERE id = %s",
                (id,),
            )

            tourn_id, judge_id, name = cursor.fetchone()

            return {"id": judge_id, "name": name, "tournament_id": tourn_id}

    @staticmethod
    def add_conflict(tournament_id: int, id: int, school: str):
        with get_cnx() as db:
            cursor = db.cursor()
            cursor.execute(
                f"INSERT INTO {conflict_table} (tournament_id, judge_id, school_name) VALUES (%s, %s, %s)",
                (tournament_id, id, school),
            )

            db.commit()

            return cursor.lastrowid

    @staticmethod
    def get_conflicts(tournament_id: int, id: int):
        with get_cnx() as db:
            cursor = db.cursor()
            cursor.execute(
                f"SELECT school_name FROM {conflict_table} WHERE judge_id = %s", (id,)
            )

            conflicts = [name for (name,) in cursor.fetchall()]

            return conflicts

    @staticmethod
    def get_ballots(tournament_id: int, judge_id: int):
        with get_cnx() as db:
            cursor = db.cursor()
            cursor.execute(
                f"SELECT id FROM {ballots_table} WHERE judge_id = %s", (judge_id,)
            )

            ballot_ids = [b_id for (b_id,) in cursor.fetchall()]

            return ballot_ids

    @staticmethod
    def get_ballot_for_round(tournament_id: int, judge_id: int, round_num: int):
        with get_cnx() as db:
            cursor = db.cursor()
            cursor.execute(
                f"SELECT ballot_id FROM {ballot_matchup_table} WHERE judge_id = %s AND round_num = %s",
                (judge_id, round_num),
            )

            ballot_ids = [b_id for (b_id,) in cursor.fetchall()]

            if len(ballot_ids) == 0:
                return None
            else:
                return ballot_ids[0]

    @staticmethod
    def set_email(judge_id: int, email: str):
        with get_cnx() as db:
            cursor = db.cursor()
            cursor.execute(
                f"""
                    UPDATE {judge_table}
                        SET email = %s
                    WHERE id = %s
                """,
                (email, judge_id),
            )

            db.commit()

    @staticmethod
    def get_email(judge_id: int):
        with get_cnx() as db:
            cursor = db.cursor()
            cursor.execute(
                f"""
                    SELECT email
                        FROM {judge_table}
                    WHERE id = %s
                """,
                (judge_id,),
            )

            (email,) = cursor.fetchone()

            return email
