class DiscoverCoreFailedException(Exception):
    def __init(self, msg="Discover Core Failed"):
        self.message = msg


class EstablishConnectionFailedException(Exception):
    def __init__(self, msg="Establish Connection Failed"):
        self.message = msg
