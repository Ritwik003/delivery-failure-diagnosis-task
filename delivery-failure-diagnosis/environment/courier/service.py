"""Public delivery API."""

from courier import retry
from courier.failures import DeliveryFailure, RetryBudgetExhausted
from courier.transport import DEFAULT_SCRIPT, Transport


class Result:
    """The outcome of one delivery.

    ``outcome`` is one of ``delivered``, ``permanent_failure`` or
    ``retries_exhausted``. ``reason`` is the failure code, or None on success.
    ``attempts`` is how many times the endpoint was called.
    """

    def __init__(self, outcome, reason, attempts, receipt=None):
        self.outcome = outcome
        self.reason = reason
        self.attempts = attempts
        self.receipt = receipt

    def __repr__(self):
        return "Result(outcome={!r}, reason={!r}, attempts={!r})".format(
            self.outcome, self.reason, self.attempts
        )


def deliver(job, transport=None, log=None):
    """Deliver one job, retrying while the failure looks worth repeating."""
    if transport is None:
        transport = Transport(DEFAULT_SCRIPT)

    _emit(log, "INFO", "courier.service", "job={} destination={}".format(job.id, job.destination))

    try:
        receipt, attempts = retry.run(
            lambda: transport.send(job), job.destination, log=log
        )
    except DeliveryFailure as failure:
        _emit(
            log,
            "INFO",
            "courier.service",
            "job={} permanent_failure ({}) after {} attempt(s)".format(
                job.id, failure.code, failure.attempts
            ),
        )
        return Result("permanent_failure", failure.code, failure.attempts)
    except RetryBudgetExhausted as exhausted:
        return Result("retries_exhausted", "upstream_unavailable", exhausted.attempts)

    return Result("delivered", None, attempts, receipt)


def _emit(log, level, source, message):
    if log is not None:
        log("{} {} {}".format(level, source, message))
