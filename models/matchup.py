from models.connection import get_cnx, tables

matchup_table = tables["matchup"]
side_table = tables["side"]
ballots_table = tables["ballot"]
full_matchup_table = tables["full_matchup"]


class Matchup:
    @staticmethod
    def add_matchup(tournament_id, round_num, pl, defense):
        with get_cnx() as db:
            cursor = db.cursor()
            cursor.execute(
                f"INSERT INTO {matchup_table} (tournament_id, round_num) VALUES (%s, %s)",
                (tournament_id, round_num),
            )
            matchup_id = cursor.lastrowid
            values = [
                (tournament_id, matchup_id, "pl", pl),
                (tournament_id, matchup_id, "def", defense),
            ]
            cursor.executemany(
                f"INSERT INTO {side_table} (tournament_id, matchup_id, side, team_num) VALUES (%s, %s, %s, %s)",
                values,
            )

            db.commit()

            return matchup_id

    @staticmethod
    def get_matchup(matchup_id):
        with get_cnx() as db:
            cursor = db.cursor()
            cursor.execute(
                f"""
                SELECT tournament_id, pl, def, round_num 
                    FROM {full_matchup_table}
                WHERE id = %s
                """,
                (matchup_id,),
            )

            (tourn_id, pl_num, def_num, round_num) = cursor.fetchone()
            return {
                "tournament_id": tourn_id,
                "pl": pl_num,
                "def": def_num,
                "round_num": round_num,
            }

    @staticmethod
    def get_ballots(matchup_id: int):
        with get_cnx() as db:
            cursor = db.cursor()
            cursor.execute(
                f"SELECT id FROM {ballots_table} WHERE matchup_id = %s", (matchup_id,)
            )

            ballot_ids = [bid for (bid,) in cursor.fetchall()]

            return ballot_ids

    @staticmethod
    def get_notes(matchup_id: int):
        with get_cnx() as db:

            cursor = db.cursor()
            cursor.execute(
                f"""
                    SELECT notes
                        FROM {matchup_table}
                    WHERE id = %s
                """,
                (matchup_id,),
            )

            (notes,) = cursor.fetchone()

            return notes

    @staticmethod
    def set_notes(matchup_id: int, notes: str):
        with get_cnx() as db:
            cursor = db.cursor()
            cursor.execute(
                f"""
                    UPDATE {matchup_table}
                        SET notes = %s
                    WHERE id = %s
                """,
                (notes, matchup_id,),
            )

            db.commit()

            return True
