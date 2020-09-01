from models.connection import db, tables

matchup_table = tables["matchup"]
side_table = tables["side"]


class Round:
    @staticmethod
    def get_matchups_for_round(tournament_id, round_num):
        cursor = db.cursor()
        cursor.execute(
            f"""SELECT id, P.team_num, D.team_num 
                FROM {matchup_table} M
                    INNER JOIN {side_table} P ON M.id = P.matchup_id
                    INNER JOIN {side_table} D ON M.id = D.matchup_id
            WHERE M.tournament_id = %s AND round_num = %s AND P.side = "pl" AND D.side = "def" """,
            (tournament_id, round_num,),
        )

        matchups = []
        for id, pl_num, def_num in cursor.fetchall():
            matchups.append({"id": id, "pl": pl_num, "def": def_num})

        return matchups
