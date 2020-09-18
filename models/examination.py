from models.connection import get_cnx, tables

examination_table = tables["examination"]


class Examination:
    @staticmethod
    def _get_info_for_exam(matchup_id: int, side: str, order: int):
        with get_cnx() as db:
            cursor = db.cursor()
            cursor.execute(
                f"""
                SELECT witness_id, attorney_id, crossing_id, witness_name
                    FROM {examination_table}
                WHERE matchup_id = %s AND side = %s AND `order` = %s
                """,
                (matchup_id, side, order),
            )

            (witness, attorney, crosser, name) = cursor.fetchone()

            return {
                "witness": witness,
                "attorney": attorney,
                "crosser": crosser,
                "name": name,
            }

    @staticmethod
    def assign_student_to_witness_order(
        matchup_id: int, side: str, order: int, student_id: int
    ):
        with get_cnx() as db:
            cursor = db.cursor()
            cursor.execute(
                f"""
                INSERT INTO {examination_table} (matchup_id, side, `order`, witness_id)
                    VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE witness_id = %s
                """,
                (matchup_id, side, order, student_id, student_id,),
            )

            db.commit()

    @staticmethod
    def get_witness_in_order(matchup_id: int, side: str, order: int):
        info = Examination._get_info_for_exam(matchup_id, side, order)
        return info["witness"]

    @staticmethod
    def assign_attorney_to_direct_order(
        matchup_id: int, side: str, order: int, student_id: int
    ):
        with get_cnx() as db:
            cursor = db.cursor()
            cursor.execute(
                f"""
                INSERT INTO {examination_table} (matchup_id, side, `order`, attorney_id)
                    VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE attorney_id = %s
                """,
                (matchup_id, side, order, student_id, student_id),
            )

            db.commit()

    @staticmethod
    def get_attorney_in_order(matchup_id: int, side: str, order: int):
        info = Examination._get_info_for_exam(matchup_id, side, order)
        return info["attorney"]

    @staticmethod
    def assign_attorney_to_cross(
        matchup_id: int, side: str, order: int, student_id: int
    ):
        with get_cnx() as db:
            cursor = db.cursor()
            cursor.execute(
                f"""
                INSERT INTO {examination_table} (matchup_id, side, `order`, crossing_id)
                    VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE crossing_id = %s
                """,
                (matchup_id, side, order, student_id, student_id),
            )

            db.commit()

    @staticmethod
    def get_attorney_crossing_witness(matchup_id: int, witness_side: str, order: int):
        info = Examination._get_info_for_exam(matchup_id, witness_side, order)
        return info["crosser"]

    @staticmethod
    def assign_witness_name(matchup_id: int, side: str, order: int, witness_name: str):
        with get_cnx() as db:
            cursor = db.cursor()
            cursor.execute(
                f"""
                INSERT INTO {examination_table} (matchup_id, side, `order`, witness_name)
                    VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE witness_name = %s
                """,
                (matchup_id, side, order, witness_name, witness_name),
            )

            db.commit()

    @staticmethod
    def get_witness_name(matchup_id: int, witness_side: str, order: int):
        info = Examination._get_info_for_exam(matchup_id, witness_side, order)

        return info["name"]
