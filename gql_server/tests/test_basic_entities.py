from gql_server.schema import schema
from .test_graphql_server import TestGraphQLServerBase

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

    def test_get_team_name(self):
        self.add_school_to_tournament("Midlands University")
        self.add_team_to_tournament(
            1001, "Midlands University", "Midlands University A"
        )

        result = schema.execute(
            f"""
            query getTeamName {{
                tournament(id: {self.tourn_id}) {{
                    team(num: {1001}) {{
                        name
                    }}
                }}
            }}
            """
        )

        team_name = result.data['tournament']['team']['name']

        self.assertEqual("Midlands University A", team_name)
