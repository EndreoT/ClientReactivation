"""Custom exceptions to provide feedback when validating client information."""


class InvalidEmail(Exception):
    """Raised when email does not contain '@' sign."""
    pass


class DateTooFarInPast(Exception):
    """Raised when date is too far in past."""
    pass


class IncorrectNumberOfTerms(Exception):
    """Raised when client list does not contain enough terms."""
    pass
