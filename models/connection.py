import mysql.connector.pooling
import os

from dotenv import load_dotenv

load_dotenv()

db_config = {
    "host": os.environ.get("host"),
    "port": os.environ.get("port"),
    "username": os.environ.get("username"),
    "password": os.environ.get("password"),
    "database": os.environ.get("database"),
}


def get_cnx():
    return mysql.connector.connect(**db_config)


tables = {
    "tournament": "Tournament",
    "school": "School",
    "team": "Team",
    "judge": "Judge",
    "conflict": "JudgeConflict",
    "matchup": "Matchup",
    "full_matchup": "FullMatchupData",
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
    "ballot_matchup_info": "BallotMatchupView",
    "notes": "Notes",
    "speech_notes": "SpeechNotes",
    "speech_notes_info": "SpeechNotesInfo",
}
