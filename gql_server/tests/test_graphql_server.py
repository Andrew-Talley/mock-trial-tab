import sys
import unittest

from itertools import chain, repeat
from os import environ

from gql_server.schema import schema
from models.tournament import Tournament

from .assertions import GraphQLTestCase


class FakeHeader:
    @staticmethod
    def get(key):
        return environ.get('code')

class FakeInfo:
    headers = FakeHeader()

class TestGraphQLServerBase(GraphQLTestCase):
    def _to_GQL_bool(self, value):
        return "true" if value else "false"
    
    def setUp(self):
        self.create_tournament()

    def tearDown(self):
        Tournament.delete_tournament(self.tourn_id)

        super().tearDown()

    def create_tournament(self):
        result = schema.execute(
            """
            mutation makeTournament {
                addTournament(name: "Test Tournament") {
                    id 
                    name
                }
            }
            """
        )
        new_tourn_data = result.data["addTournament"]
        self.tourn_id = new_tourn_data["id"]

        return new_tourn_data

    def add_school_to_tournament(self, name):
        result = schema.execute(
            f"""
            mutation addSchool {{
                addSchool(tournament: {self.tourn_id}, name: "{name}") {{
                    name
                }}
            }}
            """
        )

        new_school_data = result.data["addSchool"]

        return new_school_data

    def add_team_to_tournament(self, team_num, school, team_name):
        result = schema.execute(
            f"""
            mutation addTeam {{
                addTeam(tournament: {self.tourn_id}, school: "{school}", num: {team_num}, name: "{team_name}") {{
                    num
                    name

                    schoolName
                    tournamentId
                }}
            }}
            """
        )

        new_team = result.data["addTeam"]

        return new_team

    def add_judge_to_tournament(self, name):
        result = schema.execute(
            f"""
            mutation addJudge {{
                addJudge(tournamentId: {self.tourn_id}, name: "{name}") {{
                    id
                    name
                }}
            }}
            """
        )

        new_judge = result.data["addJudge"]

        return new_judge

    def get_judge_info(self, judge_id):
        result = schema.execute(
            f"""
            query getJudge {{
                tournament(id: {self.tourn_id}) {{
                    judge(id: {judge_id}) {{
                        id
                        name
                        email
                    }}
                }}
            }}
            """
        )

        judge = result.data["tournament"]["judge"]

        return judge

    def add_judge_conflict(self, judge_id, school):
        result = schema.execute(
            f"""
            mutation addConflict {{
                addJudgeConflict(tournamentId: {self.tourn_id}, judgeId: {judge_id}, school: "{school}") {{
                    id
                }}
            }}
            """
        )

    def add_round(self, round_num, matchups):
        serialized_matchups = [
            ("{" + ", ".join(f"{k}: {v}" for k, v in matchup.items()) + "}")
            for matchup in matchups
        ]

        serialized_matchups = ", ".join(serialized_matchups)

        result = schema.execute(
            f"""
            mutation generateRound {{
                addManualRound(tournamentId: {self.tourn_id}, matchups: [{serialized_matchups}]) {{
                    roundNum
                    matchups {{
                        id
                        pl {{
                            team {{
                                num
                            }}
                        }}
                        def {{
                            team {{
                                num
                            }}
                        }}
                    }}
                }}
            }}
            """
        )

        newRound = result.data["addManualRound"]

        serialized_matchups = [
            {"pl": match["pl"]["team"]["num"], "def": match["def"]["team"]["num"]}
            for match in newRound["matchups"]
        ]

        return [match["id"] for match in newRound["matchups"]]

    def add_student_to_team(self, team_num, student_name):
        result = schema.execute(
            f"""
            mutation addStudent {{
                addStudentToTeam(tournamentId: {self.tourn_id}, team: {team_num}, name: "{student_name}") {{
                    team {{
                        num
                    }}
                    student {{
                        id
                        name
                    }}
                }}
            }}
            """
        )

        if result.errors:
            raise Exception(result.errors)

        newTeam = result.data["addStudentToTeam"]

        return newTeam

    def assign_ballot(self, matchup_id, judge_id, note_only = False):
        result = schema.execute(
            f"""
            mutation assignBallot {{
                assignJudgeToMatchup(tournament: {self.tourn_id}, matchup: {matchup_id}, judge: {judge_id}, noteOnly: {self._to_GQL_bool(note_only)}) {{
                    id
                    noteOnly
                    judge {{
                        id
                    }}
                    matchup {{
                        id
                    }}
                }}
            }}
            """
        )

        newBallot = result.data["assignJudgeToMatchup"]

        return {
            "id": newBallot["id"],
            "judge": newBallot["judge"]["id"],
            "matchup": newBallot["matchup"]["id"],
            "note_only": newBallot["noteOnly"],
        }

    def assign_student_to_role(self, matchup, team, student, role):
        result = schema.execute(
            f"""
            mutation assignToOpening {{
                assignStudentToRole(tournamentId: {self.tourn_id}, matchup: {matchup}, team: {team}, student: {student}, role: {role}) {{
                    matchup {{
                        id
                    }}
                    student {{
                        id
                    }}
                    role
                }}
            }}
            """
        )

        assignment = result.data["assignStudentToRole"]

        return assignment

    def assign_witness_to_order(self, matchup, side, student, order):
        result = schema.execute(
            f"""
            mutation assignStudentWitnessOrder {{
                assignWitnessOrder(tournament: {self.tourn_id}, matchup: {matchup}, side: {side}, student: {student}, order: {order}) {{
                    matchup {{
                        id
                    }}
                    student {{
                        id
                    }}
                    order
                }}
            }}
            """
        )

        assignment = result.data["assignWitnessOrder"]

        return assignment

    def assign_attorney_to_order(self, matchup, side, student, order):
        result = schema.execute(
            f"""
                mutation assignAttorneyDirect {{
                    assignAttorneyToDirect(
                        tournament: {self.tourn_id}, matchup: {matchup}, side: {side}, student: {student}, order: {order}
                    ) {{
                        matchup {{
                            id
                        }}
                        student {{
                            id
                        }}
                        order
                    }}
                }}
            """
        )

        assignment = result.data['assignAttorneyToDirect']

        return assignment

    def assign_cross(self, matchup, side, student, order):
        result = schema.execute(
            f"""
            mutation assignCrossExamination {{
                assignCrossOrder(tournament: {self.tourn_id}, matchup: {matchup}, side: {side}, student: {student}, order: {order}) {{
                    matchup {{
                        id
                    }}
                    student {{
                        id
                    }}
                    team {{
                        num
                    }}
                    order
                }}
            }}
            """
        )

        assignment = result.data['assignCrossOrder']

        return assignment

    def assign_witness_name(self, matchup, side, order, name):
        result = schema.execute(
            f"""
            mutation assignWitnessName {{
                assignWitnessName(tournament: {self.tourn_id}, matchup: {matchup}, side: {side}, order: {order}, witness: "{name}") {{
                    matchup {{
                        id
                    }}
                    witnessName
                }}
            }}
            """
        )

        assignment = result.data['assignWitnessName']

        return assignment

    def create_midlands_a(self):
        self.add_school_to_tournament("Midlands University")
        self.add_team_to_tournament(
            1001, "Midlands University", "Midlands University A"
        )

    def add_default_team_matrix(self):
        self.add_school_to_tournament("Midlands University")
        self.add_school_to_tournament("Midlands State University")

        self.add_team_to_tournament(
            1001, "Midlands University", "Midlands University A"
        )
        self.add_team_to_tournament(
            1002, "Midlands University", "Midlands University B"
        )

        self.add_team_to_tournament(
            1101, "Midlands State University", "Midlands State University A"
        )
        self.add_team_to_tournament(
            1102, "Midlands State University", "Midlands State University B"
        )

    def add_elizabeth_bayes(self):
        result = self.add_student_to_team(1001, "Elizabeth Bayes")
        return result["student"]["id"]

    def add_num_students_to_team(self, num_students, team):
        students = []

        for student_num in range(num_students):
            result = self.add_student_to_team(team, f"Student {student_num}")
            students.append(result['student']['id'])

        return students

    def add_default_r1_setup(self):
        self.add_default_team_matrix()
        matchups = self.add_round(
            1, [{"pl": 1001, "def": 1101}, {"pl": 1002, "def": 1102}]
        )
        return matchups

    def add_one_matchup_setup(self):
        self.add_school_to_tournament("Midlands University")
        self.add_school_to_tournament("Midlands State University")

        self.add_team_to_tournament(
            1001, "Midlands University", "Midlands University A"
        )
        self.add_team_to_tournament(
            1101, "Midlands State University", "Midlands State University A"
        )

        matchup = self.add_round(1, [{"pl": 1001, "def": 1101}])

        return matchup[0]

    def add_one_matchup_w_judge(self):
        matchup = self.add_one_matchup_setup()
        judge = self.add_judge_to_tournament("John G. Roberts, Jr.")['id']
        ballot = self.assign_ballot(matchup, judge)['id']

        return (matchup, judge, ballot)

    def add_default_judges(self):
        roberts = self.add_judge_to_tournament("John G. Roberts, Jr.")
        avenatti = self.add_judge_to_tournament("Michael Avenatti")

        return [roberts, avenatti]

    def _speech_assignment(self, ballot, side, speech, score):
        return f"assignSpeechScore(ballot: {ballot}, side: {side}, speech: {speech}, score: {score})"

    def assign_speech_score(self, ballot, side, speech, score):
        result = schema.execute(
            f"""
            mutation openingScore {{
                {self._speech_assignment(ballot, side, speech, score)}
            }}
            """,
            None,
            FakeInfo
        )
        
        score = result.data['assignSpeechScore']

        return score

    def _exam_assignment(self, ballot, side, exam, witness, cross, score):
        return f"assignExamScore(ballot: {ballot}, side: {side}, exam: {exam}, witness: {self._to_GQL_bool(witness)}, cross: {self._to_GQL_bool(cross)}, score: {score})"

    def assign_exam_score(self, ballot, side, exam, witness, cross, score):
        result = schema.execute(
            f"""
                mutation addWitnessScore {{
                    {self._exam_assignment(ballot, side, exam, witness, cross, score)}
                }}
            """,
            None,
            FakeInfo
        )

        return result.data['assignExamScore']

    def assign_full_round(self, ballot, pd):
        pl_scores = chain(repeat(10, pd), repeat(9))
        def_scores = repeat(9)

        side_scores = {
            "PL": pl_scores,
            "DEF": def_scores
        }

        def speech_assignment(side, speech):
            return self._speech_assignment(ballot, side, speech, next(side_scores[side]))

        def exam_assignment(side, exam, witness, cross):
            return self._exam_assignment(ballot, side, exam, witness, cross, next(side_scores[side]))
        
        def pl_full_exam(exam):
            return f"""
                wDir{exam}: {exam_assignment("PL", exam, True, False)}
                aDir{exam}: {exam_assignment("PL", exam, False, False)}
                wCr{exam}: {exam_assignment("PL", exam, True, True,)}
                aCr{exam}: {exam_assignment("DEF", exam, False, True)}
            """

        def def_full_exam(exam):
            return f"""
                dWDir{exam}: {exam_assignment("DEF", exam, True, False,)}
                dADir{exam}: {exam_assignment("DEF", exam, False, False)}
                dWCr{exam}: {exam_assignment("DEF", exam, True, True)}
                dACr{exam}: {exam_assignment("PL", exam, False, True)}
            """

        new_line = "\n"

        schema.execute(
            f"""
            mutation fullRound {{
                pOpen: {speech_assignment("PL", "OPENING")}
                dOpen: {speech_assignment("DEF", "OPENING")}
                {new_line.join(pl_full_exam(exam) for exam in range(1, 4))}
                {new_line.join(def_full_exam(exam) for exam in range(1, 4))}
                pClose: {speech_assignment("PL", "CLOSING")}
                dClose: {speech_assignment("DEF", "CLOSING")}
            }}
            """,
            None,
            FakeInfo
        )

    def assign_speech_notes(self, ballot, side, speech, notes):
        result = schema.execute(f"""
            mutation assignNotes {{
                assignSpeechNotes(ballot: {ballot}, side: {side}, speech: {speech}, notes: "{notes}")
            }}
        """)

        return result.data['assignSpeechNotes']

    def assign_exam_notes(self, ballot, side, exam, witness, cross, notes):
        result = schema.execute(f"""
            mutation assignExamNotes {{
                assignExamNotes(ballot: {ballot}, side: {side}, exam: {exam}, witness: {self._to_GQL_bool(witness)}, cross: {self._to_GQL_bool(cross)}, notes: "{notes}")
            }}
        """)

        return result.data['assignExamNotes']
