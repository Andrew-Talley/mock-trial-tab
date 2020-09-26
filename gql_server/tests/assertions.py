import unittest
from gql_server.schema import schema

def expected_len(type, expected, found):
    return f"Expected to see {expected} {type}s, but had {found} instead"

class GraphQLTestCase(unittest.TestCase):
    tourn_id: int

    def assertStringIsInt(self, number):
        try:
            int(number)
            return True
        except:
            return False

    def get_all_tournaments(self):
        result = schema.execute(
            f"""
            query getTournaments {{
                tournaments {{
                id
                name
                }}
            }}
            """
        )

        return result.data["tournaments"]

    def assertHasNumSchools(self, num_schools):
        result = schema.execute(
            f"""
            query numSchools {{
                tournament(id: {self.tourn_id}) {{
                schools {{
                    name
                }}
                }}
            }}
            """
        )

        school_list = result.data["tournament"]["schools"]
        true_num_schools = len(school_list)

        self.assertEqual(
            true_num_schools,
            num_schools,
            expected_len("school", num_schools, true_num_schools),
        )

    def assertHasNumTeams(self, num_teams):
        result = schema.execute(
            f"""
            query numTeams {{
                tournament(id: {self.tourn_id}) {{
                teams {{
                    name
                }}
                }}
            }}
            """
        )

        team_list = result.data["tournament"]["teams"]
        true_num_teams = len(team_list)

        self.assertEqual(
            true_num_teams, num_teams, expected_len("team", num_teams, true_num_teams)
        )

    def assertSchoolHasNumTeams(self, school, num_teams):
        result = schema.execute(
            f"""
            query numTeams {{
                tournament(id: {self.tourn_id}) {{
                school(name: "{school}") {{
                    name
                    teams {{
                    num
                    }}
                }}
                }}
            }}
            """
        )

        teams = result.data["tournament"]["school"]["teams"]
        true_num_teams = len(teams)

        self.assertEqual(
            num_teams, true_num_teams, expected_len("team", num_teams, true_num_teams)
        )

    def assertSchoolContainsTeam(self, school, team_num, team_name):
        result = schema.execute(
            f"""
            query numTeams {{
                tournament(id: {self.tourn_id}) {{
                school(name: "{school}") {{
                    teams {{
                    num
                    name
                    }}
                }}
                }}
            }}
            """
        )
        teams = result.data["tournament"]["school"]["teams"]
        has_team = any(
            team["name"] == team_name and team["num"] == team_num for team in teams
        )

        team_ids = ", ".join(str(team["num"]) for team in teams)
        self.assertTrue(
            has_team,
            f"Team {team_num} not found. Team numbers: {team_ids} (also check the names)",
        )

    def assertTournamentHasNumJudges(self, num_judges):
        result = schema.execute(
            f"""
            query numTeams {{
                tournament(id: {self.tourn_id}) {{
                judges {{
                    id
                }}
                }}
            }}
            """
        )

        judges = result.data["tournament"]["judges"]
        true_num_judges = len(judges)

        self.assertEqual(
            num_judges,
            true_num_judges,
            expected_len("judge", num_judges, true_num_judges),
        )

    def assertJudgeHasConflict(self, judge_id, school):
        result = schema.execute(
            f"""
            query judgeConflict {{
                tournament(id: {self.tourn_id}) {{
                    judge(id: {judge_id}) {{
                        conflicts {{
                            name
                        }}
                    }}
                }}
            }}
            """
        )

        conflicts = result.data["tournament"]["judge"]["conflicts"]
        self.assertTrue(
            any(conflict["name"] == school for conflict in conflicts),
            f"School {school} not found in conflicts for judge {judge_id}",
        )

    def assertJudgeIsListed(self, judge_id):
        result = schema.execute(
            f"""
            query judgeList {{
                tournament(id: {self.tourn_id}) {{
                    judges {{
                        id
                    }}
                }}
            }}
            """
        )

        judges = result.data['tournament']['judges']
        self.assertTrue(
            any(judge['id'] == judge_id for judge in judges), f"Judge {judge_id} not found in {self.tourn_id}"
        )

    def assertHasNumRounds(self, num_rounds):
        result = schema.execute(
            f"""
            query roundsInTournament {{
                tournament(id: {self.tourn_id}) {{
                    rounds {{
                        roundNum
                    }}
                }}
            }}
            """
        )

        rounds = result.data["tournament"]["rounds"]
        true_num_rounds = len(rounds)

        self.assertEqual(
            num_rounds,
            true_num_rounds,
            expected_len("round", num_rounds, true_num_rounds),
        )

    def assertHasRound(self, round_num):
        result = schema.execute(
            f"""
            query roundInTournament {{
                tournament(id: {self.tourn_id}) {{
                    round(num: {round_num}) {{
                        roundNum
                    }}
                }}
            }}
            """
        )

        found_round = result.data['tournament']['round']

        self.assertEqual(found_round['roundNum'], round_num)

    def assertJudgeHasBallot(self, judge_id, ballot_id):
        result = schema.execute(
            f"""
            query judgeBallots {{
                tournament(id: {self.tourn_id}) {{
                    judge(id: {judge_id}) {{
                        ballots {{
                            id
                        }}
                    }}
                }}
            }}
            """
        )

        true_ballots = result.data["tournament"]["judge"]["ballots"]

        has_ballot = any(ballot["id"] == ballot_id for ballot in true_ballots)
        self.assertTrue(
            has_ballot, f"Ballot {ballot_id} not found in ballots for judge {judge_id}"
        )

    def assertMatchupHasBallot(self, matchup_id, ballot_id):
        result = schema.execute(
            f"""
            query matchupBallots {{
                tournament(id: {self.tourn_id}) {{
                    matchup(id: {matchup_id}) {{
                        ballots {{
                            id
                        }}
                    }}
                }}
            }}
            """
        )

        true_ballots = result.data["tournament"]["matchup"]["ballots"]

        has_ballot = any(ballot["id"] == ballot_id for ballot in true_ballots)
        self.assertTrue(
            has_ballot, f"Ballot {ballot_id} not found in ballots for judge {ballot_id}"
        )

    def assertHasMatchup(self, matchup_id, pl_num, def_num):
        result = schema.execute(
            f"""
            query matchupTest {{
                tournament(id: {self.tourn_id}) {{
                    matchup(id: {matchup_id}) {{
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

        matchup = result.data["tournament"]["matchup"]

        self.assertEqual(matchup["pl"]["team"]["num"], pl_num, "π num does not match")
        self.assertEqual(matchup["def"]["team"]["num"], def_num, "∆ num does not match")

    def _get_students(self, team_num):
        result = schema.execute(
            f"""
            query getStudents {{
                tournament(id: {self.tourn_id}) {{
                    team(num: {team_num}) {{
                        students {{
                            id
                            name
                        }}
                    }}
                }}
            }}
            """
        )

        students = result.data["tournament"]["team"]["students"]

        return students

    def assertTeamHasNumStudents(self, team_num, num_students):
        students_list = self._get_students(team_num)
        true_num_students = len(students_list)

        self.assertEqual(
            num_students,
            true_num_students,
            expected_len("student", num_students, true_num_students),
        )

    def assertTeamHasStudent(self, team_num, student_name):
        students = [student["name"] for student in self._get_students(team_num)]
        self.assertIn(
            student_name,
            students,
            f"{student_name} not found in students for team {team_num}",
        )

    def assertStudentHasRole(self, student_id, role, matchup, side):
        result = schema.execute(
            f"""
            query getRole {{
                tournament(id: {self.tourn_id}) {{
                    matchup(id: {matchup}) {{
                        team(side: {side}) {{
                            attorney(role: {role}) {{
                                student {{
                                    id
                                }}
                            }}
                        }}
                    }}
                }}
            }}
            """
        )

        student_in_role = result.data["tournament"]["matchup"]["team"]["attorney"]['student']
        self.assertIsNotNone(student_in_role, f"No student assigned to {role}")
        self.assertEqual(
            student_in_role["id"],
            student_id,
            f"Student {student_id} does not have role {role}",
        )

    def assertWitnessGoesInOrder(self, student_id, order, matchup, side):
        result = schema.execute(
            f"""
            query getWitnessOrder {{
                tournament(id: {self.tourn_id}) {{
                    matchup(id: {matchup}) {{
                        team(side: {side}) {{
                            witness(order: {order}) {{
                                student {{
                                    id
                                }}
                            }}
                        }}
                    }}
                }}
            }}
            """
        )

        student = result.data["tournament"]['matchup']['team']['witness']['student']

        self.assertEqual(student['id'], student_id)

    def assertAttorneyDirectsInOrder(self, student_id, order, matchup, side):
        result = schema.execute(
            f"""
            query getAttorneyOrder {{
                tournament(id: {self.tourn_id}) {{
                    matchup(id: {matchup}) {{
                        team(side: {side}) {{
                            attorney(order: {order}) {{
                                student {{
                                    id
                                }}
                            }}
                        }}
                    }}
                }}
            }}
            """
        )

        attorney = result.data['tournament']['matchup']['team']['attorney']['student']
        self.assertEqual(attorney['id'], student_id)

    def assertAttorneyIsCrossingWitness(self, student_id, order, witness_side, matchup):
        result = schema.execute(
            f"""
            query getCrossingAttorney {{
                tournament(id: {self.tourn_id}) {{
                    matchup(id: {matchup}) {{
                        team(side: {witness_side}) {{
                            attorney(crossingWitnessNum: {order}) {{
                                student {{
                                    id
                                }}
                            }}
                        }}
                    }}
                }}
            }}
            """
        )

        attorney = result.data['tournament']['matchup']['team']['attorney']['student']

        self.assertEqual(attorney['id'], student_id)

    def assertHasWitnessName(self, name, matchup, side, order):
        result = schema.execute(
            f"""
            query getWitnessName {{
                tournament(id: {self.tourn_id}) {{
                    matchup(id: {matchup}) {{
                        team(side: {side}) {{
                            witness(order: {order}) {{
                                witnessName
                            }}
                        }}
                    }}
                }}
            }}
            """
        )

        witnessName = result.data['tournament']['matchup']['team']['witness']['witnessName']
        
        self.assertEqual(name, witnessName)

    def assertSpeechHasScore(self, score, speech, side, ballot):
        result = schema.execute(
            f"""
            query getSpeechScore {{
                tournament(id: {self.tourn_id}) {{
                    ballot(id: {ballot}) {{
                        side(side: {side}) {{
                            speech(speech: {speech})
                        }}
                    }}
                }}
            }}
            """
        )

        print(result)

        true_score = result.data['tournament']['ballot']['side']['speech']

        self.assertEqual(score, true_score)

    def assertExamHasScore(self, score, cross, witness, exam, side, ballot):
        role = "WITNESS" if witness else "ATTORNEY"
        exam_type = "CROSS" if cross else "DIRECT"

        result = schema.execute(
            f"""
            query getExamScore {{
                tournament(id: {self.tourn_id}) {{
                    ballot(id: {ballot}) {{
                        side(side: {side}) {{
                            exam(order: {exam}, role: {role}, type: {exam_type})
                        }}
                    }}
                }}
            }}
            """
        )

        true_score = result.data['tournament']['ballot']['side']['exam']

        self.assertEqual(true_score, score)

    def assertBallotSideHasSum(self, ballot, side, score):
        result = schema.execute(
            f"""
            query getSideSum {{
                tournament(id: {self.tourn_id}) {{
                    ballot(id: {ballot}) {{
                        side(side: {side}) {{
                            sum
                        }}
                    }}
                }}
            }}
            """
        )

        side_sum = result.data['tournament']['ballot']['side']['sum']

        self.assertEqual(score, side_sum)

    def assertBallotHasPD(self, ballot, side, pd):
        result = schema.execute(
            f"""
            query getPD {{
                tournament(id: {self.tourn_id}) {{
                    ballot(id: {ballot}) {{
                        pd(side: {side})
                    }}
                }}
            }}
            """
        )

        true_pd = result.data['tournament']['ballot']['pd']

        self.assertEqual(pd, true_pd)

    def assertBallotIsDone(self, ballot, done=True):
        result = schema.execute(
            f"""
            query ballotIsDone {{
                tournament(id: {self.tourn_id}) {{
                    ballot(id: {ballot}) {{
                        complete
                    }}
                }}
            }}
            """
        )

        is_complete = result.data['tournament']['ballot']['complete']
        
        self.assertEqual(done, is_complete)

    def assertTeamHasRecord(self, team_num, wins, losses, ties):
        result = schema.execute(
            f"""
            query record {{
                tournament(id: {self.tourn_id}) {{
                    team(num: {team_num}) {{
                        wins
                        losses
                        ties
                    }}
                }}
            }}
            """
        )

        record = result.data['tournament']['team']

        self.assertEqual(wins, record['wins'])
        self.assertEqual(losses, record['losses'])
        self.assertEqual(ties, record['ties'])

    def assertSpeechHasNotes(self, ballot, side, speech, notes):
        result = schema.execute(f"""
            query getOpeningNote {{
                tournament(id: {self.tourn_id}) {{
                    ballot(id: {ballot}) {{
                        side(side: {side}) {{
                            speechNotes(speech: {speech})
                        }}
                    }}
                }}
            }}
        """)

        self.assertEqual(result.data['tournament']['ballot']['side']['speechNotes'], notes)

    def assertExamHasNotes(self, notes, cross, witness, exam, side, ballot):
        role = "WITNESS" if witness else "ATTORNEY"
        exam_type = "CROSS" if cross else "DIRECT"

        result = schema.execute(f"""
            query getOpeningNote {{
                tournament(id: {self.tourn_id}) {{
                    ballot(id: {ballot}) {{
                        side(side: {side}) {{
                            examNotes(order: {exam}, role: {role}, type: {exam_type})
                        }}
                    }}
                }}
            }}
        """)

        self.assertEqual(result.data['tournament']['ballot']['side']['examNotes'], notes)