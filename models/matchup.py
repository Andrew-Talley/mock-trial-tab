from models.connection import db, tables

matchup_table = tables["matchup"]
side_table = tables["side"]
ballots_table = tables["ballot"]


class Matchup:
    @staticmethod
    def add_matchup(tournament_id, round_num, pl, defense):
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
        cursor = db.cursor()
        cursor.execute(
            f"""SELECT M.tournament_id, P.team_num, D.team_num, round_num 
                FROM {matchup_table} M
                    INNER JOIN {side_table} P ON M.id = P.matchup_id
                    INNER JOIN {side_table} D ON M.id = D.matchup_id
            WHERE id = %s AND P.side = "pl" AND D.side = "def" """,
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
        cursor = db.cursor()
        cursor.execute(
            f"SELECT id FROM {ballots_table} WHERE matchup_id = %s", (matchup_id,)
        )

        ballot_ids = [id for (id,) in cursor.fetchall()]

        return ballot_ids
