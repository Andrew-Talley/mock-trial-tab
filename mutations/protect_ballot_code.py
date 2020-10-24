from os import environ


def protect_ballot_code(info):
    try:
        passed_code = info.context.headers.get("Ballot-Code")
        true_code = environ.get("code")
        assert passed_code == true_code

    except:
        raise Exception("User not authorized to modify ballot")
