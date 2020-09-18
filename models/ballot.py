from models.connection import get_cnx, tables

ballot_table = tables["ballot"]
ballot_info = tables["ballot_info"]


class Ballot:
    @staticmethod
    def create_ballot(matchup_id, judge_id):
        with get_cnx() as db:
            cursor = db.cursor()
            cursor.execute(
                f"INSERT INTO {ballot_table} (matchup_id, judge_id) VALUES (%s, %s)",
                (matchup_id, judge_id),
            )

            db.commit()

            return cursor.lastrowid

    @staticmethod
    def set_is_complete(ballot_id, complete):
        with get_cnx() as db:
            cursor = db.cursor()
            cursor.execute(
                f"""
                UPDATE {ballot_table}
                    SET complete = {1 if complete else 0}
                WHERE id = %s
                """,
                (ballot_id,)
            )

            db.commit()

    @staticmethod
    def get_is_complete(ballot_id):
        with get_cnx() as db:
            cursor = db.cursor()
            cursor.execute(
                f"SELECT complete FROM {ballot_table} WHERE id = %s", (ballot_id,)
            )

            (complete,) = cursor.fetchone()

            return complete == 1

    @staticmethod
    def get_judge_for_ballot(ballot_id):
        with get_cnx() as db:
            cursor = db.cursor()
            cursor.execute(
                f"""
                SELECT judge_id
                    FROM {ballot_table}
                WHERE id = %s
                """,
                (ballot_id,),
            )

            (judge,) = cursor.fetchone()

            return judge

    @staticmethod
    def get_matchup_for_ballot(ballot_id):
        with get_cnx() as db:
            cursor = db.cursor()
            cursor.execute(
                f"""
                SELECT matchup_id
                    FROM {ballot_table}
                WHERE id = %s
                """,
                (ballot_id,)
            )

            (matchup,) = cursor.fetchone()
            
            return matchup
