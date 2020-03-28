class AuthenticationError(Exception):
    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        if self.message:
            return 'AuthenticationError : {0} '.format(self.message)
        else:
            return ("AuthenticationError - Username or Password is incorrect. "
                    "To try again execute "
                    "FitnessFirstSG.auth(username, password)")

class MissingCredentialsError(Exception):
    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        if self.message:
            return 'MissingCredentialsError : {0} '.format(self.message)
        else:
            return ("MissingCredentialsError - "
                    "Please input username and password."
                    "To try again execute "
                    "FitnessFirstSG.auth(username, password)")

class RequestsError(Exception):
    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        if self.message:
            return ('RequestsError : Request returned with status code {0} '
                    ).format(self.message)
        else:
            return ('RequestsError - '
                    'Requests returned with status code not equal to 200')
