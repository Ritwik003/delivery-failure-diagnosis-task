"""Failure types raised by the delivery path."""


class DeliveryFailure(Exception):
    """A single delivery attempt was rejected.

    ``status`` is the transport status the endpoint replied with. ``code`` is
    the failure code carried in the response body.
    """

    def __init__(self, status, code, message=None):
        super().__init__(message or "{} {}".format(status, code))
        self.status = status
        self.code = code
        self.attempts = None


class RetryBudgetExhausted(Exception):
    """Every attempt in the retry budget was spent without a decision."""

    def __init__(self, destination, attempts):
        super().__init__(
            "destination {} did not accept the delivery after {} attempts".format(
                destination, attempts
            )
        )
        self.destination = destination
        self.attempts = attempts
