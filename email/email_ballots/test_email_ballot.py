from .email_ballot import email_ballots

class TestEmailBallot:
  @staticmethod
  def create_info(id: int, tourn_id: int, matchup_notes: str, code: int, judge_name: str, email: str):
    return {
      "id": 1,
      "tournament_id": tourn_id,
      "matchup": {
        "notes": matchup_notes,
      },
      "code": code,
      "judge": {
        "name": judge_name,
        "email": email
      }
    }

  @staticmethod
  def test_email():
    email_ballots([
      TestEmailBallot.create_info(1, 4114, "*Zoom link*: https://cmu.zoom.us/j/93124206933", 1776, "Cayden Codel", "ccodel@andrew.cmu.edu"),
      TestEmailBallot.create_info(2, 4114, "*Zoom link*: https://cmu.zoom.us/j/fake-data", 1776, "Other Judge", "ccodel@andrew.cmu.edu"),
    ])


if __name__ == "__main__":
  TestEmailBallot.test_email()