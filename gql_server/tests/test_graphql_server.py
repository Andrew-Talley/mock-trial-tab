import sys
import unittest
from gql_server.schema import schema
from models.tournament import Tournament

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
    result = schema.execute(f"""
      query getTournaments {{
        tournaments {{
          id
          name
        }}
      }}
    """)

    return result.data['tournaments']

  def assertHasNumSchools(self, num_schools):
    result = schema.execute(f"""
      query numSchools {{
        tournament(id: {self.tourn_id}) {{
          schools {{
            name
          }}
        }}
      }}
    """)

    school_list = result.data['tournament']['schools']
    true_num_schools = len(school_list)

    self.assertEqual(true_num_schools, num_schools, expected_len("school", num_schools, true_num_schools))

  def assertHasNumTeams(self, num_teams):
    result = schema.execute(f"""
      query numTeams {{
        tournament(id: {self.tourn_id}) {{
          teams {{
            name
          }}
        }}
      }}
    """)

    team_list = result.data['tournament']['teams']
    true_num_teams = len(team_list)

    self.assertEqual(true_num_teams, num_teams, expected_len("team", num_teams, true_num_teams))

  def assertSchoolHasNumTeams(self, school, num_teams):
    result = schema.execute(f"""
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
    """)

    teams = result.data['tournament']['school']['teams']
    true_num_teams = len(teams)

    self.assertEqual(num_teams, true_num_teams, expected_len("team", num_teams, true_num_teams))

  def assertSchoolContainsTeam(self, school, team_num, team_name):
    result = schema.execute(f"""
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
    """)
    teams = result.data['tournament']['school']['teams']
    has_team = any(team['name'] == team_name and team['num'] == team_num for team in teams)
    
    team_ids = ", ".join(str(team['num']) for team in teams)
    self.assertTrue(has_team, f"Team {team_num} not found. Team numbers: {team_ids} (also check the names)")

  def assertTournamentHasNumJudges(self, num_judges):
    result = schema.execute(f"""
      query numTeams {{
        tournament(id: {self.tourn_id}) {{
          judges {{
            id
          }}
        }}
      }}
    """)
    
    judges = result.data['tournament']['judges']
    true_num_judges = len(judges)

    self.assertEqual(num_judges, true_num_judges, expected_len("judge", num_judges, true_num_judges))

  def assertJudgeHasConflict(self, judge_id, school):
    result = schema.execute(f"""
      query judgeConflict {{
        tournament(id: {self.tourn_id}) {{
          judge(id: {judge_id}) {{
            conflicts {{
              name
            }}
          }}
        }}
      }}
    """)

    conflicts = result.data['tournament']['judge']['conflicts']
    self.assertTrue(any(conflict['name'] == school for conflict in conflicts), f"School {school} not found in conflicts for judge {judge_id}")

  def assertHasNumRounds(self, num_rounds):
    result = schema.execute(f"""
      query roundsInTournament {{
        tournament(id: {self.tourn_id}) {{
          rounds {{
            roundNum
          }}
        }}
      }}
    """)

    rounds = result.data['tournament']['rounds']
    true_num_rounds = len(rounds)

    self.assertEqual(num_rounds, true_num_rounds, expected_len("round", num_rounds, true_num_rounds))

  def assertJudgeHasBallot(self, judge_id, ballot_id):
    result = schema.execute(f"""
      query judgeBallots {{
        tournament(id: {self.tourn_id}) {{
          judge(id: {judge_id}) {{
            ballots {{
              id
            }}
          }}
        }}
      }}
    """)

    true_ballots = result.data['tournament']['judge']['ballots']

    has_ballot = any(ballot['id'] == ballot_id for ballot in true_ballots)
    self.assertTrue(has_ballot, f"Ballot {ballot_id} not found in ballots for judge {judge_id}")

  def assertMatchupHasBallot(self, matchup_id, ballot_id):
    result = schema.execute(f"""
      query matchupBallots {{
        tournament(id: {self.tourn_id}) {{
          matchup(id: {matchup_id}) {{
            ballots {{
              id
            }}
          }}
        }}
      }}
    """)

    true_ballots = result.data['tournament']['matchup']['ballots']

    has_ballot = any(ballot['id'] == ballot_id for ballot in true_ballots)
    self.assertTrue(has_ballot, f"Ballot {ballot_id} not found in ballots for judge {ballot_id}")
    

class TestGraphQLServer(GraphQLTestCase):
  def tearDown(self):
    Tournament.delete_tournament(self.tourn_id)

    return super().tearDown()

  def create_tournament_test(self):
    result = schema.execute("""
      mutation makeTournament {
        addTournament(name: "Test Tournament") {
          id 
          name
        }
      }
    """)
    new_tourn_data = result.data['addTournament']
    self.tourn_id = new_tourn_data['id']

    self.assertStringIsInt(self.tourn_id)
    self.assertEqual(new_tourn_data['name'], 'Test Tournament')

  def add_school_to_tournament(self, name):
    result = schema.execute(f"""
      mutation addSchool {{
        addSchool(tournament: {self.tourn_id}, name: "{name}") {{
          name
        }}
      }}
    """)

    new_school_data = result.data['addSchool']

    self.assertEqual(new_school_data['name'], name)
    
    return new_school_data['name']

  def get_all_tournaments_test(self):
    tournaments = self.get_all_tournaments()
    new_tournament = tournaments[0]

    self.assertEqual(new_tournament['name'], "Test Tournament")

  def add_team_to_tournament(self, team_num, school, team_name):
    result = schema.execute(f"""
      mutation addTeam {{
        addTeam(tournament: {self.tourn_id}, school: "{school}", num: {team_num}, name: "{team_name}") {{
          num
          name

          schoolName
          tournamentId
        }}
      }}
    """)

    new_team = result.data['addTeam']

    self.assertEqual(new_team['num'], team_num)
    self.assertEqual(new_team['name'], team_name)
    self.assertEqual(new_team['schoolName'], school)
    self.assertEqual(new_team['tournamentId'], self.tourn_id)

  def add_judge_to_tournament(self, name):
    result = schema.execute(f"""
      mutation addJudge {{
        addJudge(tournamentId: {self.tourn_id}, name: "{name}") {{
          id
          name
        }}
      }}
    """)

    new_judge = result.data['addJudge']

    self.assertStringIsInt(new_judge['id'])
    self.assertEqual(new_judge['name'], name)

    return new_judge['id']

  def get_judge_test(self, judge_id, judge_name):
    result = schema.execute(f"""
      query getJudge {{
        tournament(id: {self.tourn_id}) {{
          judge(id: {judge_id}) {{
            name
          }}
        }}
      }}
    """)

    judge = result.data['tournament']['judge']

    self.assertEqual(judge['name'], judge_name)

  def add_judge_conflict(self, judge_id, school):
    result = schema.execute(f"""
      mutation addConflict {{
        addJudgeConflict(tournamentId: {self.tourn_id}, judgeId: "{judge_id}", school: "{school}") {{
          id
        }}
      }}
    """)

    self.assertJudgeHasConflict(judge_id, school)

  def add_round(self, round_num, matchups):
    serialized_matchups = [
      ("{" + ", ".join(f"{k}: {v}" for k,v in matchup.items()) + "}") for matchup in matchups
    ]

    serialized_matchups = ", ".join(serialized_matchups)

    result = schema.execute(f"""
      mutation generateRound {{
        addManualRound(tournamentId: {self.tourn_id}, matchups: [{serialized_matchups}]) {{
          roundNum
          matchups {{
            id
            pl {{
              num
            }}
            def {{
              num
            }}
          }}
        }}
      }}
    """)

    newRound = result.data['addManualRound']
    
    self.assertEqual(newRound['roundNum'], round_num)

    serialized_matchups = [{"pl": match['pl']['num'], "def": match['def']['num']} for match in newRound['matchups']]
    self.assertEqual(matchups, serialized_matchups)

    return [match['id'] for match in newRound['matchups']]

  def assign_ballot(self, matchup_id, judge_id):
    result = schema.execute(f"""
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
    """)

    newBallot = result.data['assignJudgeToMatchup']
    true_judge_id = newBallot['judge']['id']
    true_matchup_id = newBallot['matchup']['id']
    self.assertEqual(judge_id, true_judge_id, "judge_id does not match true judge_id")
    self.assertEqual(matchup_id, true_matchup_id, "judge_id does not match true judge_id")

    return newBallot['id']

  def find_matchup_test(self, id, pl_num, def_num):
    result = schema.execute(f"""
      query matchupTest {{
        tournament(id: {self.tourn_id}) {{
          matchup(id: {id}) {{
            pl {{
              num
            }}
            def {{
              num
            }}
          }}
        }}
      }}
    """)

    print(result)

    matchup = result.data['tournament']['matchup']

    self.assertEqual(matchup['pl']['num'], pl_num, "π num does not match")
    self.assertEqual(matchup['def']['num'], def_num, "∆ num does not match")

  def test_everything(self):
    self.create_tournament_test()
    self.get_all_tournaments_test()

    self.assertHasNumSchools(0)
    self.add_school_to_tournament("Midlands University")
    self.assertHasNumSchools(1)
    self.add_school_to_tournament("Midlands State University")
    self.assertHasNumSchools(2)

    self.assertHasNumTeams(0)
    self.add_team_to_tournament(1001, "Midlands University", "Midlands University A")
    self.assertHasNumTeams(1)
    self.add_team_to_tournament(1101, "Midlands State University", "Midlands State University A")
    self.assertHasNumTeams(2)

    self.assertSchoolHasNumTeams("Midlands University", 1)
    self.assertSchoolContainsTeam("Midlands University", 1001, "Midlands University A")
    self.add_team_to_tournament(1002, "Midlands University", "Midlands University B")
    self.assertSchoolHasNumTeams("Midlands University", 2)
    self.assertSchoolContainsTeam("Midlands University", 1002, "Midlands University B")

    self.assertSchoolHasNumTeams("Midlands State University", 1)
    self.assertSchoolContainsTeam("Midlands State University", 1101, "Midlands State University A")
    self.add_team_to_tournament(1102, "Midlands State University", "Midlands State University B")
    self.assertSchoolHasNumTeams("Midlands State University", 2)
    self.assertSchoolContainsTeam("Midlands State University", 1102, "Midlands State University B")

    self.assertTournamentHasNumJudges(0)
    roberts_id = self.add_judge_to_tournament("John G. Roberts, Jr.")
    self.assertTournamentHasNumJudges(1)
    avenatti_id = self.add_judge_to_tournament("Michael Avenatti") # Do they have Zoom in prison?
    self.assertTournamentHasNumJudges(2)

    self.get_judge_test(roberts_id, "John G. Roberts, Jr.")
    self.add_judge_conflict(roberts_id, "Midlands University")

    self.assertHasNumRounds(0)
    matchups = self.add_round(1, [{"pl": 1001, "def": 1101}, {"pl": 1002, "def": 1102}])
    self.assertHasNumRounds(1)
    self.find_matchup_test(matchups[0], 1001, 1101)

    new_ballot = self.assign_ballot(matchups[0], roberts_id)
    self.assertJudgeHasBallot(roberts_id, new_ballot)
    self.assertMatchupHasBallot(matchups[0], new_ballot)
