from typing import Literal
from models.connection import get_cnx, tables

score_table = tables["scores"]
speech_table = tables["speech"]
exam_table = tables["exam"]

speech_data_table = tables["speech_data"]
exam_data_table = tables["exam_data"]
sum_table = tables["ballot_side_sum"]


class BallotSections:
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
    def _add_single_section(ballot_id, side):
        with get_cnx() as db:
            cursor = db.cursor()
            cursor.execute(
                f"""
                INSERT INTO {score_table} (ballot_id, pl)
                    VALUES (%s, %s)
                """,
                (ballot_id, BallotSections._sql_pl(side)),
            )

            db.commit()

            return cursor.lastrowid

    @staticmethod
    def _add_exam_section(ballot_id, side, exam_num, role, exam_type):
        new_score_id = BallotSections._add_single_section(ballot_id, side)

        with get_cnx() as db:
            cursor = db.cursor()

            sql_attorney = BallotSections._sql_attorney(role)
            sql_cross = BallotSections._sql_cross(exam_type)

            cursor.execute(
                f"""
                    INSERT INTO 
                        {exam_table} (ballot_score_id, exam_num, attorney, `cross`)
                    VALUES (%s, %s, %s, %s)
                """,
                (new_score_id, exam_num, sql_attorney, sql_cross),
            )

            db.commit()

        return new_score_id

    @staticmethod
    def _add_speech_section(ballot_id, side, speech):
        new_score_id = BallotSections._add_single_section(ballot_id, side)

        with get_cnx() as db:
            cursor = db.cursor()

            cursor.execute(
                f"""
                    INSERT INTO
                        {speech_table} (ballot_score_id, opening)
                    VALUES (%s, %s)
                """,
                (new_score_id, BallotSections._sql_opening(speech)),
            )

            db.commit()

        return new_score_id

    @staticmethod
    def _set_section_score(section_id: int, new_score: int):
        with get_cnx() as db:
            cursor = db.cursor()

            cursor.execute(
                f"""
                    UPDATE {score_table}
                        SET score = %s
                    WHERE id = %s
                """,
                (new_score, section_id),
            )

            db.commit()

    @staticmethod
    def _set_section_note(section_id, note, db_cnx=None):
        with get_cnx() as db:
            cursor = db.cursor()
            cursor.execute(
                f"""
                    UPDATE {score_table}
                        SET note = %s
                    WHERE id = %s
                """,
                (note, section_id),
            )

            db.commit()

    @staticmethod
    def get_speech_section(
        ballot_id: int, side: Literal["pl", "def"], speech: Literal["open", "close"]
    ):
        with get_cnx() as db:
            cursor = db.cursor()

            sql_pl = BallotSections._sql_pl(side)
            sql_open = BallotSections._sql_opening(speech)

            cursor.execute(
                f"""
                    SELECT score, note, id
                        FROM {speech_data_table}
                    WHERE ballot_id = %s AND pl = %s AND opening = %s
                """,
                (ballot_id, sql_pl, sql_open,),
            )

            result = cursor.fetchone()

            if result is None:
                return None

            score, note, score_id = result

            return {"score": score, "notes": note, "id": score_id}

    @staticmethod
    def set_speech_score(
        ballot_id: int,
        side: Literal["pl", "def"],
        speech: Literal["open", "close"],
        score: int,
    ):
        existing_row = BallotSections.get_speech_section(ballot_id, side, speech)
        if existing_row is None:
            section_id = BallotSections._add_speech_section(ballot_id, side, speech)
            BallotSections._set_section_score(section_id, score)
            return section_id
        else:
            BallotSections._set_section_score(existing_row["id"], score)
            return existing_row["id"]

    @staticmethod
    def get_exam_section(ballot_id, side, exam_num, role, exam_type):
        with get_cnx() as db:
            cursor = db.cursor()

            sql_attorney = BallotSections._sql_attorney(role)
            sql_cross = BallotSections._sql_cross(exam_type)
            sql_pl = BallotSections._sql_pl(side)

            cursor.execute(
                f"""
                    SELECT id, score, note
                        FROM {exam_data_table}
                    WHERE ballot_id = %s AND exam_num = %s AND attorney = %s AND `cross` = %s AND pl = %s
                """,
                (ballot_id, exam_num, sql_attorney, sql_cross, sql_pl),
            )

            results = cursor.fetchall()

            if len(results) == 0:
                return None

            for (score_id, score, note) in results:
                pass

            return {"id": score_id, "score": score, "notes": note}

    @staticmethod
    def set_exam_score(ballot_id: int, side, exam_num, role, exam_type, score):
        cur_score = BallotSections.get_exam_section(
            ballot_id, side, exam_num, role, exam_type
        )

        if cur_score is not None:
            BallotSections._set_section_score(cur_score["id"], score)
            return {"id": cur_score["id"], "score": score}
        else:
            section_id = BallotSections._add_exam_section(
                ballot_id, side, exam_num, role, exam_type
            )
            BallotSections._set_section_score(section_id, score)
            return {"id": section_id, "score": score}

    @staticmethod
    def get_sum(ballot_id, side):
        with get_cnx() as db:
            cursor = db.cursor()

            sql_pl = BallotSections._sql_pl(side)

            cursor.execute(
                f"""
                    SELECT side_sum
                        FROM {sum_table}
                    WHERE ballot_id = %s AND pl = %s
                """,
                (ballot_id, sql_pl),
            )

            try:
                (score,) = cursor.fetchone()
                return score
            except:
                return None

    @staticmethod
    def set_speech_notes(
        ballot_id: int,
        side: Literal["pl", "def"],
        speech: Literal["open", "close"],
        notes: str,
    ):
        cur_speech = BallotSections.get_speech_section(ballot_id, side, speech)

        section_id = (
            cur_speech["id"]
            if cur_speech is not None
            else BallotSections._add_speech_section(ballot_id, side, speech)
        )

        BallotSections._set_section_note(section_id, notes)

    @staticmethod
    def set_exam_notes(ballot_id: int, side, exam_num, role, exam_type, notes):
        existing_id = BallotSections.get_exam_section(
            ballot_id, side, exam_num, role, exam_type
        )

        true_id = (
            existing_id["id"]
            if existing_id is not None
            else BallotSections._add_exam_section(
                ballot_id, side, exam_num, role, exam_type
            )
        )

        BallotSections._set_section_note(true_id, notes)
