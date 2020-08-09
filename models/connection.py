import mysql.connector

db = mysql.connector.connect(
  host="localhost",
  port="8889",
  username="root",
  password="root",
  database="mock_trial_db"
)

tables = {
  "tournament": "Tournament",
  "school": "School",
  "team": "Team",
  "judge": "Judge",
  "conflict": "JudgeConflict",
  "matchup": "Matchup",
  "ballot": "Ballot"
}