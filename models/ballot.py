from models.connection import get_cnx, tables

ballot_table = tables["ballot"]
ballot_info = tables["ballot_info"]
ranks_table = tables["ranks"]


class Ballot:
    @staticmethod
    def _bool_to_SQL(witness: bool):
        return 1 if witness else 0

    @staticmethod
    def create_ballot(matchup_id, judge_id, presiding = False, note_only = False):
        with get_cnx() as db:
            cursor = db.cursor()
            cursor.execute(
                f"""
                INSERT INTO {ballot_table} 
                    (matchup_id, judge_id, presiding, note_only) 
                VALUES (%s, %s, %s, %s)
                """,
                (matchup_id, judge_id, Ballot._bool_to_SQL(presiding), Ballot._bool_to_SQL(note_only)),
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
                (ballot_id,),
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
                (ballot_id,),
            )

            (matchup,) = cursor.fetchone()

            return matchup

    @staticmethod
    def set_rank_for_ballot(ballot_id, witness: bool, rank, student):
        with get_cnx() as db:
            cursor = db.cursor()
            cursor.execute(
                f"""
                INSERT INTO {ranks_table} (ballot_id, rank, witness, student)
                    VALUES (%s, %s, %s, %s)

                ON DUPLICATE KEY UPDATE student = %s
                """,
                (ballot_id, rank, Ballot._bool_to_SQL(witness), student, student),
            )

            db.commit()

    @staticmethod
    def get_rank_for_ballot(ballot_id, witness: bool, rank):
        with get_cnx() as db:
            cursor = db.cursor()
            cursor.execute(
                f"""
                    SELECT student
                        FROM {ranks_table}
                    WHERE ballot_id = %s AND witness = %s AND rank = %s
                """,
                (ballot_id, Ballot._bool_to_SQL(witness), rank),
            )

            try:
                (sid,) = cursor.fetchone()
                return sid
            except:
                return None

    @staticmethod
    def get_ballot(ballot_id):
        with get_cnx() as db:
            cursor = db.cursor()
            cursor.execute(
                f"""
                    SELECT presiding, note_only
                        FROM {ballot_table}
                    WHERE id = %s
                """,
                (ballot_id,)
            )

            (preside, note_only) = cursor.fetchone()

            return {
                "presiding": preside == 1,
                "note_only": note_only == 1
            }

    @staticmethod
    def delete_ballot(ballot_id):
        with get_cnx() as db:
            cursor = db.cursor()
            cursor.execute(
                f"""
                    DELETE FROM {ballot_table}
                        WHERE id = %s
                """,
                (ballot_id,)
            )
            
            db.commit()

            return True
