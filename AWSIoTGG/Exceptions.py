class establishConnectionFailedException(Exception):
    def __init__(self, msg="Establish Connection Failed"):
        self.message = msg
