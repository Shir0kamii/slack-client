class SlackError(Exception):
    pass

class SlackNo(SlackError):
    pass

class SlackMissingAPI(SlackError):
    pass

class SlackNotFound(SlackError):
    pass
