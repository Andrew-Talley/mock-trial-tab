import mysql.connector

db = mysql.connector.connect(
    host="localhost",
    port="8889",
    username="root",
    password="root",
    database="mock_trial_db",
)

tables = {
    "tournament": "Tournament",
    "school": "School",
    "team": "Team",
    "judge": "Judge",
    "conflict": "JudgeConflict",
    "matchup": "Matchup",
    "side": "MatchupSide",
    "ballot": "Ballot",
    "student": "Student",
    "role": "AttorneyRole",
    "examination": "Examination",
    "scores": "BallotScore",
    "speech": "SpeechScore",
    "exam": "ExamScore",
    "speech_data": "SpeechData",
    "exam_data": "ExamData",
    "ballot_side_sum": "BallotSideSum",
    "ballot_info": "BallotInfo",
}
