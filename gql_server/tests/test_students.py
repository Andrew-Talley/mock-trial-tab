import unittest

from gql_server.schema import schema
from .test_graphql_server import TestGraphQLServerBase

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

    def test_can_query_empty_students(self):
        matchup = self.add_one_matchup_setup()

        self.assertStudentHasRole(None, "CLOSER", matchup, "PL")
        self.assertWitnessGoesInOrder(None, 1, matchup, "PL")

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

    def test_can_find_null_witness(self):
        matchup = self.add_one_matchup_setup()
        self.assertHasWitnessName(None, matchup, "PL", 1)

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
