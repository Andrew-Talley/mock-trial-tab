from typing import Literal
from models.connection import db, tables

score_table = tables["scores"]
speech_table = tables["speech"]
exam_table = tables["exam"]

speech_data_table = tables["speech_data"]
exam_data_table = tables["exam_data"]
sum_table = tables["ballot_side_sum"]


class Scores:
    @staticmethod
    def _sql_pl(side: Literal["pl", "def"]):
        return 1 if side == "pl" else 0

    @staticmethod
    def _sql_opening(speech: Literal["open", "close"]):
        return 1 if speech == "open" else 0

    @staticmethod
    def _sql_attorney(role: Literal["witness", "attorney"]):
        return 1 if role == "attorney" else 0

    @staticmethod
    def _sql_cross(exam_type: Literal["direct", "cross"]):
        return 1 if exam_type == "cross" else 0

    @staticmethod
    def _add_single_score(ballot_id, side, score):
        cursor = db.cursor()
        sql_side = Scores._sql_pl(side)
        cursor.execute(
            f"""
            INSERT INTO {score_table} (ballot_id, pl, score)
                VALUES (%s, %s, %s)
            """,
            (ballot_id, sql_side, score),
        )

        return cursor.lastrowid

    @staticmethod
    def _add_speech_score(ballot_id, side, speech, score):
        new_ballot_score = Scores._add_single_score(ballot_id, side, score)

        cursor = db.cursor()

        sql_opening = Scores._sql_opening(speech)
        cursor.execute(
            f"""
            INSERT INTO {speech_table} (ballot_score_id, opening)
                VALUES (%s, %s)
            """,
            (new_ballot_score, sql_opening),
        )

        db.commit()

        return new_ballot_score

    @staticmethod
    def _update_speech_score(score_id, score):
        cursor = db.cursor()

        cursor.execute(
            f"""
                UPDATE {score_table}
                    SET score = %s
                WHERE id = %s
            """,
            (score, score_id),
        )

        db.commit()

    @staticmethod
    def set_speech_score(
        ballot_id: int,
        side: Literal["pl", "def"],
        speech: Literal["open", "close"],
        score: int,
    ):
        existing_row = Scores.get_speech_score(ballot_id, side, speech)
        if existing_row is None:
            return Scores._add_speech_score(ballot_id, side, speech, score)
        else:
            Scores._update_speech_score(existing_row["id"], score)
            return existing_row["id"]

    @staticmethod
    def get_speech_score(
        ballot_id: int, side: Literal["pl", "def"], speech: Literal["open", "close"]
    ):
        cursor = db.cursor()
        sql_pl = Scores._sql_pl(side)
        sql_opening = Scores._sql_opening(speech)

        cursor.execute(
            f"""
                SELECT score, id
                    FROM {speech_data_table}
                WHERE ballot_id = %s AND pl = %s AND opening = %s
            """,
            (ballot_id, sql_pl, sql_opening),
        )

        result = cursor.fetchone()

        if result is None:
            return None

        score, score_id = result

        return {"score": score, "id": score_id}

    @staticmethod
    def _update_exam_score(score_id: int, new_score: int):
        cursor = db.cursor()

        cursor.execute(
            f"""
                UPDATE {score_table}
                    SET score = %s
                WHERE id = %s
            """,
            (new_score, score_id),
        )

    @staticmethod
    def _add_exam_score(ballot_id, side, exam_num, role, exam_type, score):
        new_score_id = Scores._add_single_score(ballot_id, side, score)

        cursor = db.cursor()

        sql_attorney = Scores._sql_attorney(role)
        sql_cross = Scores._sql_cross(exam_type)

        cursor.execute(
            f"""
                INSERT INTO {exam_table} (ballot_score_id, exam_num, attorney, `cross`)
                    VALUES (%s, %s, %s, %s)
            """,
            (new_score_id, exam_num, sql_attorney, sql_cross),
        )

        db.commit()

        return {"id": new_score_id, "score": score}

    @staticmethod
    def set_exam_score(ballot_id: int, side, exam_num, role, exam_type, score):
        cur_score = Scores.get_exam_score(ballot_id, side, exam_num, role, exam_type)

        if cur_score is not None:
            Scores._update_exam_score(cur_score["id"], score)
            return {"id": cur_score["id"], "score": score}
        else:
            return Scores._add_exam_score(
                ballot_id, side, exam_num, role, exam_type, score
            )

    @staticmethod
    def get_exam_score(ballot_id, side, exam_num, role, exam_type):
        cursor = db.cursor()

        sql_attorney = Scores._sql_attorney(role)
        sql_cross = Scores._sql_cross(exam_type)
        sql_pl = Scores._sql_pl(side)

        cursor.execute(
            f"""
                SELECT id, score
                    FROM {exam_data_table}
                WHERE ballot_id = %s AND exam_num = %s AND attorney = %s AND `cross` = %s AND pl = %s
            """,
            (ballot_id, exam_num, sql_attorney, sql_cross, sql_pl),
        )

        results = cursor.fetchall()

        if len(results) == 0:
            return None

        for (score_id, score) in results:
            pass

        return {"id": score_id, "score": score}

    @staticmethod
    def get_sum(ballot_id, side):
        cursor = db.cursor()

        sql_pl = Scores._sql_pl(side)

        cursor.execute(
            f"""
                SELECT side_sum
                    FROM {sum_table}
                WHERE ballot_id = %s AND pl = %s
            """,
            (ballot_id, sql_pl),
        )

        (score,) = cursor.fetchone()

        return score
