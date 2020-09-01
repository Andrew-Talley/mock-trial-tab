import sys
import unittest
from gql_server.schema import schema
from models.tournament import Tournament

from .assertions import GraphQLTestCase

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
                        name
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
                addJudgeConflict(tournamentId: {self.tourn_id}, judgeId: "{judge_id}", school: "{school}") {{
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

    def assign_ballot(self, matchup_id, judge_id):
        result = schema.execute(
            f"""
            mutation assignBallot {{
                assignJudgeToMatchup(matchup: {matchup_id}, judge: {judge_id}) {{
                id
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
        result = self.add_student_to_team(1001, "Elizebth Bayes")
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

    def assign_speech_score(self, ballot, side, speech, score):
        result = schema.execute(
            f"""
            mutation openingScore {{
                assignSpeechScore(ballot: {ballot}, side: {side}, speech: {speech}, score: {score})
            }}
            """
        )
        
        score = result.data['assignSpeechScore']

        return score

    def assign_exam_score(self, ballot, side, exam, witness, cross, score):
        result = schema.execute(
            f"""
                mutation addWitnessScore {{
                    assignExamScore(ballot: {ballot}, side: {side}, exam: {exam}, witness: {self._to_GQL_bool(witness)}, cross: {self._to_GQL_bool(cross)}, score: {score})
                }}
            """
        )

        return result.data['assignExamScore']

    def assign_full_round(self, ballot, pd):
        return

class TestTournamentsTeamsAndSchools(TestGraphQLServerBase):
    def test_create_tournament(self):
        new_tourn_data = self.create_tournament()

        self.assertStringIsInt(self.tourn_id)
        self.assertEqual(new_tourn_data["name"], "Test Tournament")

    def test_get_all_tournamnets(self):
        tournaments = self.get_all_tournaments()
        new_tournament = tournaments[0]

        self.assertEqual(new_tournament["name"], "Test Tournament")

    def test_starts_with_no_schools(self):
        self.assertHasNumSchools(0)

    def test_add_school(self):
        new_school = self.add_school_to_tournament("Midlands University")
        self.assertEqual(new_school["name"], "Midlands University")
        self.assertHasNumSchools(1)

    def test_add_multiple_schools(self):
        self.add_school_to_tournament("Midlands University")
        self.add_school_to_tournament("Midlands State University")
        self.assertHasNumSchools(2)

    def test_starts_with_no_teams(self):
        self.assertHasNumTeams(0)

    def test_school_starts_with_no_teams(self):
        self.add_school_to_tournament("Midlands University")
        self.assertSchoolHasNumTeams("Midlands University", 0)

    def test_add_team(
        self, school="Midlands University", team="Midlands University A", num=1001
    ):
        self.add_school_to_tournament("Midlands University")
        new_team = self.add_team_to_tournament(num, school, team)

        self.assertEqual(new_team["num"], num)
        self.assertEqual(new_team["name"], team)
        self.assertEqual(new_team["schoolName"], school)
        self.assertEqual(new_team["tournamentId"], self.tourn_id)

        self.assertSchoolHasNumTeams(school, 1)
        self.assertSchoolContainsTeam(school, num, team)

    def test_add_multiple_teams(self):
        self.add_school_to_tournament("Midlands University")
        self.add_school_to_tournament("Midlands State University")
        self.add_team_to_tournament(
            1001, "Midlands University", "Midlands University A"
        )
        self.assertHasNumTeams(1)

        self.add_team_to_tournament(
            1101, "Midlands State University", "Midlands State University A"
        )
        self.assertHasNumTeams(2)

    def test_school_starts_without_team(self):
        self.test_add_school()
        with self.assertRaises(AssertionError):
            self.assertSchoolContainsTeam(
                "Midlands University", 1001, "Midlands University A"
            )

    def test_school_has_teams_after_add(self):
        self.add_school_to_tournament("Midlands University")
        self.add_team_to_tournament(
            1001, "Midlands University", "Midlands University A"
        )
        self.assertSchoolContainsTeam(
            "Midlands University", 1001, "Midlands University A"
        )

class TestMatchups(TestGraphQLServerBase):
    def test_starts_with_no_rounds(self):
        self.assertHasNumRounds(0)

    def test_can_add_manual_round(self):
        self.add_default_team_matrix()
        matchups = self.add_round(
            1, [{"pl": 1001, "def": 1101}, {"pl": 1002, "def": 1102}]
        )
        self.assertHasNumRounds(1)
        self.assertHasMatchup(matchups[0], 1001, 1101)
        self.assertHasMatchup(matchups[1], 1002, 1102)

class TestJudges(TestGraphQLServerBase):
    def test_tournament_starts_with_no_judges(self):
        self.assertTournamentHasNumJudges(0)

    def test_can_add_judge(self):
        roberts = self.add_judge_to_tournament("John G. Roberts, Jr.")
        self.assertStringIsInt(roberts["id"])
        self.assertEqual(roberts["name"], "John G. Roberts, Jr.")
        self.assertTournamentHasNumJudges(1)

    def test_can_add_multiple_judges(self):
        self.add_judge_to_tournament("John G. Roberts, Jr.")
        self.add_judge_to_tournament("Michael Avenatti")  # Do they have Zoom in prison?
        self.assertTournamentHasNumJudges(2)

    def test_get_judge_works(self):
        roberts = self.add_judge_to_tournament("John G. Roberts, Jr.")
        roberts_id = roberts["id"]

        found_info = self.get_judge_info(roberts["id"])
        self.assertEqual(found_info["name"], "John G. Roberts, Jr.")

    def test_add_judge_conflict(self):
        roberts = self.add_judge_to_tournament("John G. Roberts, Jr.")
        self.add_judge_conflict(roberts["id"], "Midlands University")
        self.assertJudgeHasConflict(roberts["id"], "Midlands University")

    def test_can_assign_ballot(self):
        matchup_id = self.add_one_matchup_setup()
        judge_id = self.add_judge_to_tournament("John G. Roberts, Jr.")['id']

        new_ballot = self.assign_ballot(matchup_id, judge_id)

        self.assertEqual(
            judge_id, new_ballot["judge"], "judge_id does not match true judge_id"
        )
        self.assertEqual(
            matchup_id, new_ballot["matchup"], "judge_id does not match true judge_id"
        )

    def test_assigned_ballot_appears_in_graph(self):
        matchup_id, judge_id, new_ballot = self.add_one_matchup_w_judge()

        self.assertJudgeHasBallot(judge_id, new_ballot)
        self.assertMatchupHasBallot(matchup_id, new_ballot)

class TestStudents(TestGraphQLServerBase):
    def test_teams_start_with_no_students(self):
        self.create_midlands_a()
        self.assertTeamHasNumStudents(1001, 0)

    def test_can_add_students(self):
        self.create_midlands_a()

        result = self.add_student_to_team(1001, "Elizabeth Bayes")
        self.assertEqual(result['student']['name'], "Elizabeth Bayes")

        self.assertTeamHasStudent(1001, "Elizabeth Bayes")
        self.assertTeamHasNumStudents(1001, 1)

    @unittest.skipIf(True, "Throws an error that ruins debug")
    def test_cannot_add_duplicate_student(self):
        self.create_midlands_a()
        self.add_student_to_team(1001, "Elizabeth Bayes")

        with self.assertRaises(BaseException):
            stuff = self.add_student_to_team(1001, "Elizabeth Bayes")

    def test_can_assign_student_to_closer(self):
        matchup = self.add_one_matchup_setup()
        bayes_id = self.add_elizabeth_bayes()

        assignment = self.assign_student_to_role(matchup, 1001, bayes_id, "CLOSER")

        matchup_id = assignment["matchup"]["id"]
        self.assertEqual(matchup, matchup_id, "matchup id is incorrect")

        student_id = assignment["student"]["id"]
        self.assertEqual(student_id, bayes_id, "Student id is incorrect")

        role = assignment["role"]
        self.assertEqual(role, "CLOSER")

        self.assertStudentHasRole(bayes_id, "CLOSER", matchup, "PL")

    def test_can_assign_full_lineup(self):
        matchup = self.add_one_matchup_setup()
        students = self.add_num_students_to_team(3, 1001)

        roles = ["OPENER", "MIDDLE", "CLOSER"]
        for student, role in zip(students, roles):
            self.assign_student_to_role(matchup, 1001, student, role)

        for student, role in zip(students, roles):
            self.assertStudentHasRole(student, role, matchup, "PL")

    def test_can_assign_student_to_w1(self):
        matchup = self.add_one_matchup_setup()
        bayes_id = self.add_elizabeth_bayes()

        assignment = self.assign_witness_to_order(matchup, "PL", bayes_id, 1)

        self.assertEqual(assignment["matchup"]["id"], matchup)
        self.assertEqual(assignment["student"]["id"], bayes_id)
        self.assertEqual(assignment["order"], 1)
        
        self.assertWitnessGoesInOrder(bayes_id, 1, matchup, "PL")

    def test_can_assign_full_witness_lineup(self):
        matchup = self.add_one_matchup_setup()
        students = self.add_num_students_to_team(3, 1001)
        orders = range(1, 4)

        for order, student in zip(orders, students):
            self.assign_witness_to_order(matchup, "PL", student, order)

        for order, student in zip(orders, students):
            self.assertWitnessGoesInOrder(student, order, matchup, "PL")

    def test_can_assign_attorney_to_direct_witness(self):
        matchup = self.add_one_matchup_setup()
        bayes_id = self.add_elizabeth_bayes()
            
        assignment = self.assign_attorney_to_order(matchup, "PL", bayes_id, 1)

        self.assertEqual(assignment['matchup']['id'], matchup)
        self.assertEqual(assignment['student']['id'], bayes_id)
        self.assertEqual(assignment['order'], 1)

        self.assertAttorneyDirectsInOrder(bayes_id, 1, matchup, "PL")

    def test_can_assign_all_attorney_directs(self):
        matchup = self.add_one_matchup_setup()
        students = self.add_num_students_to_team(3, 1001)

        for order, student in enumerate(students):
            self.assign_attorney_to_order(matchup, "PL", student, order)

        for order, student in enumerate(students):
            self.assertAttorneyDirectsInOrder(student, order, matchup, "PL")

    def test_can_assign_cross_examination(self):
        matchup = self.add_one_matchup_setup()
        student, = self.add_num_students_to_team(1, 1101)

        assignment = self.assign_cross(matchup, "PL", student, 1)

        self.assertEqual(assignment['matchup']['id'], matchup)
        self.assertEqual(assignment['student']['id'], student)
        self.assertEqual(assignment['team']['num'], 1101)
        self.assertEqual(assignment['order'], 1)

        self.assertAttorneyIsCrossingWitness(student, 1, "PL", matchup)

    def test_can_assign_all_crosses(self):
        matchup = self.add_one_matchup_setup()
        students = self.add_num_students_to_team(3, 1101)

        for order, attorney in enumerate(students):
            self.assign_cross(matchup, "PL", attorney, order)

        for order, attorney in enumerate(students):
            self.assertAttorneyIsCrossingWitness(attorney, order, "PL", matchup)

    def test_can_assign_witness_name(self):
        matchup = self.add_one_matchup_setup()

        assignment = self.assign_witness_name(matchup, "PL", 1, "Danny Kosack")

        self.assertEqual(assignment['matchup']['id'], matchup)
        self.assertEqual(assignment['witnessName'], "Danny Kosack")

        self.assertHasWitnessName("Danny Kosack", matchup, "PL", 1)

    def test_can_assign_full_call_order(self):
        matchup = self.add_one_matchup_setup()

        lineup = ["Kelly Doos", "Dr. Ron Quincy", "Kai Washington"]

        for order, witness in enumerate(lineup):
            self.assign_witness_name(matchup, "PL", order, witness)

        for order, witness in enumerate(lineup):
            self.assertHasWitnessName(witness, matchup, "PL", order)

    def test_can_create_case_in_chief(self):
        matchup = self.add_one_matchup_setup()
        students = self.add_num_students_to_team(6, 1001)
        crossers = self.add_num_students_to_team(3, 1101)
        lineup = ["Kelly Doos", "Dr. R. Quincy", "Kai Washington"]

        attorneys = students[:3]
        witnesses = students[3:]

        for order, (witness, attorney, crosser, name) in enumerate(zip(witnesses, attorneys, crossers, lineup)):
            self.assign_witness_to_order(matchup, "PL", witness, order)
            self.assign_attorney_to_order(matchup, "PL", attorney, order)
            self.assign_cross(matchup, "PL", crosser, order)
            self.assign_witness_name(matchup, "PL", order, name)

        for order, (witness, attorney, crosser, name) in enumerate(zip(witnesses, attorneys, crossers, lineup)):
            self.assertWitnessGoesInOrder(witness, order, matchup, "PL")
            self.assertAttorneyDirectsInOrder(attorney, order, matchup, "PL")
            self.assertAttorneyIsCrossingWitness(crosser, order, "PL", matchup)
            self.assertHasWitnessName(name, matchup, "PL", order)

class TestScoring(TestGraphQLServerBase):
    def test_can_score_and_modify_opening(self):
        _, judge, ballot = self.add_one_matchup_w_judge()

        score = self.assign_speech_score(ballot, "PL", "OPENING", 10)
        self.assertEqual(score, 10)
        self.assertSpeechHasScore(10, "OPENING", "PL", ballot)

        score = self.assign_speech_score(ballot, "PL", "OPENING", 8)
        self.assertEqual(score, 8)
        self.assertSpeechHasScore(8, "OPENING", "PL", ballot)

    def test_can_score_and_modify_closing(self):
        _, judge, ballot = self.add_one_matchup_w_judge()

        self.assign_speech_score(ballot, "PL", "CLOSING", 10)
        self.assertSpeechHasScore(10, "CLOSING", "PL", ballot)

        self.assign_speech_score(ballot, "PL", "CLOSING", 8)
        self.assertSpeechHasScore(8, "CLOSING", "PL", ballot)

    def test_can_score_atty_direct(self):
        _, judge, ballot = self.add_one_matchup_w_judge()

        score = self.assign_exam_score(ballot, "PL", 1, False, False, 8)

        self.assertEqual(score, 8)
        self.assertExamHasScore(8, False, False, 1, "PL", ballot)

        self.assign_exam_score(ballot, "PL", 1, False, False, 10)
        self.assertExamHasScore(10, False, False, 1, "PL", ballot)

    def test_can_score_atty_cross(self):
        _, judge, ballot = self.add_one_matchup_w_judge()

        score = self.assign_exam_score(ballot, "PL", 1, False, True, 8)
        self.assertExamHasScore(8, True, False, 1, "PL", ballot)

    def test_can_sum_scores(self):
        _, judge, ballot = self.add_one_matchup_w_judge()

        self.assign_exam_score(ballot, "PL", 1, False, False, 10)
        self.assertBallotSideHasSum(ballot, "PL", 10)

    def test_sum_updates(self):
        _, judge, ballot = self.add_one_matchup_w_judge()

        self.assign_exam_score(ballot, "PL", 1, False, False, 10)
        self.assertBallotSideHasSum(ballot, "PL", 10)

        self.assign_exam_score(ballot, "PL", 1, False, False, 8)
        self.assertBallotSideHasSum(ballot, "PL", 8)

    def test_can_sum_speeches(self):
        _, judge, ballot = self.add_one_matchup_w_judge()

        self.assign_speech_score(ballot, "PL", "OPENING", 10)
        self.assertBallotSideHasSum(ballot, "PL", 10)

    def test_can_sum_exams_and_speeches(self):
        _, judge, ballot = self.add_one_matchup_w_judge()

        self.assign_speech_score(ballot, "PL", "OPENING", 6)
        self.assign_exam_score(ballot, "PL", 1, False, False, 9)
        self.assertBallotSideHasSum(ballot, "PL", 15)

    def test_sums_sides_independently(self):
        _, judge, ballot = self.add_one_matchup_w_judge()

        self.assign_speech_score(ballot, "PL", "OPENING", 8)
        self.assign_speech_score(ballot, "DEF", "OPENING", 9)

        self.assertBallotSideHasSum(ballot, "PL", 8)
        self.assertBallotSideHasSum(ballot, "DEF", 9)

    def test_finds_pd(self):
        _, judge, ballot = self.add_one_matchup_w_judge()

        self.assign_speech_score(ballot, "PL", "OPENING", 8)
        self.assign_speech_score(ballot, "DEF", "OPENING", 9)

        self.assertBallotHasPD(ballot, "PL", -1)

    def test_full_round_scoring(self):
        _, judge, ballot = self.add_one_matchup_w_judge()

        self.assign_speech_score(ballot, "PL", "OPENING", 8)
        self.assign_speech_score(ballot, "DEF", "OPENING", 9)

        self.assertBallotSideHasSum(ballot, "PL", 8)
        self.assertBallotSideHasSum(ballot, "DEF", 9)

        PL_WIT_DX = 9
        PL_ATTY_DX = 8
        PL_WIT_CX = 9
        DEF_ATTY_CX = 7

        pl_exam_sum = PL_WIT_DX + PL_ATTY_DX + PL_WIT_CX

        for exam in range(1, 4):
            with self.subTest(f"PL Exam {exam}"):
                self.assign_exam_score(ballot, "PL", exam, True, False, PL_WIT_DX)
                self.assign_exam_score(ballot, "PL", exam, False, False, PL_ATTY_DX)
                self.assign_exam_score(ballot, "PL", exam, True, True, PL_WIT_CX)
                self.assign_exam_score(ballot, "DEF", exam, False, True, DEF_ATTY_CX)

                self.assertBallotSideHasSum(ballot, "PL", (pl_exam_sum * exam) + 8)
                self.assertBallotSideHasSum(ballot, "DEF", (DEF_ATTY_CX * exam) + 9)

        pl_recess_score = 8 + (pl_exam_sum * 3)
        def_recess_score = 9 + (DEF_ATTY_CX * 3)

        self.assertBallotSideHasSum(ballot, "PL", pl_recess_score)
        self.assertBallotSideHasSum(ballot, "DEF", def_recess_score)
        self.assertBallotHasPD(ballot, "PL", pl_recess_score - def_recess_score)

        DEF_WIT_DX = 8
        DEF_WIT_CX = 7
        DEF_ATTY_DX = 9
        PL_ATTY_CX = 10

        def_exam_sum = DEF_WIT_DX + DEF_ATTY_DX + DEF_WIT_CX

        for exam in range(1, 4):
            with self.subTest(f"DEF Exam {exam}"):
                self.assign_exam_score(ballot, "DEF", exam, True, False, DEF_WIT_DX)
                self.assign_exam_score(ballot, "DEF", exam, False, False, DEF_ATTY_DX)
                self.assign_exam_score(ballot, "DEF", exam, True, True, DEF_WIT_CX)
                self.assign_exam_score(ballot, "PL", exam, False, True, PL_ATTY_CX)

                self.assertBallotSideHasSum(ballot, "PL", pl_recess_score + (exam * PL_ATTY_CX))
                self.assertBallotSideHasSum(ballot, "DEF", def_recess_score + (exam * def_exam_sum))

        pl_pre_closing_score = pl_recess_score + (3 * PL_ATTY_CX)
        def_pre_closing_score = def_recess_score + (3 * def_exam_sum)

        self.assertBallotSideHasSum(ballot, "PL", pl_pre_closing_score)
        self.assertBallotSideHasSum(ballot, "DEF", def_pre_closing_score)
        self.assertBallotHasPD(ballot, "PL", pl_pre_closing_score - def_pre_closing_score)

        self.assertBallotIsDone(ballot, False)

        self.assign_speech_score(ballot, "PL", "CLOSING", 9)
        self.assign_speech_score(ballot, "DEF", "CLOSING", 10)

        expected_pd = (pl_pre_closing_score - def_pre_closing_score) - 1

        self.assertBallotHasPD(ballot, "PL", expected_pd)

        self.assertBallotIsDone(ballot, True)
