class BotException(Exception):
    """Base exception"""


class NoArguments(BotException):
    """Raised if no arguments were provided"""


class NotFound(BotException):
    pass


class NotAllowed(BotException):
    """Raised if user has no required permissions"""


class NoPermissions(BotException):
    """Raised if bot has no required permissions"""


class AlreadyExists(BotException):
    pass


class Success(BotException):
    """Raised upon success"""
