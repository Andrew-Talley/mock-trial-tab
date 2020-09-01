from models.connection import db, tables

ballot_table = tables["ballot"]
ballot_info = tables["ballot_info"]


class Ballot:
    @staticmethod
    def create_ballot(matchup_id, judge_id):
        cursor = db.cursor()
        cursor.execute(
            f"INSERT INTO {ballot_table} (matchup_id, judge_id) VALUES (%s, %s)",
            (matchup_id, judge_id),
        )

        db.commit()

        return cursor.lastrowid

    @staticmethod
    def get_is_complete(ballot_id):
        cursor = db.cursor()
        cursor.execute(
            f"SELECT complete FROM {ballot_info} WHERE id = %s", (ballot_id,)
        )

        (complete,) = cursor.fetchone()

        return complete
