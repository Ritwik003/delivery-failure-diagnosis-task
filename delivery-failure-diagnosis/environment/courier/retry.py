"""Retry loop around a single delivery attempt.

Backoff is computed and reported but never slept on: the service is driven by
a scheduler that owns the wall clock.
"""

from courier.failures import DeliveryFailure, RetryBudgetExhausted
from courier.policy import is_retryable

MAX_ATTEMPTS = 5
BASE_BACKOFF_SECONDS = 1


def backoff_seconds(attempt):
    """Exponential backoff for the given attempt number, starting at 1."""
    return BASE_BACKOFF_SECONDS * (2 ** (attempt - 1))


def run(operation, destination, max_attempts=MAX_ATTEMPTS, log=None):
    """Call ``operation`` until it succeeds, fails permanently, or runs out.

    Returns ``(value, attempts)`` on success. Re-raises ``DeliveryFailure``
    when the failure is permanent, with ``attempts`` set. Raises
    ``RetryBudgetExhausted`` once the budget is spent.
    """
    attempts = 0
    while attempts < max_attempts:
        attempts += 1
        try:
            return operation(), attempts
        except DeliveryFailure as failure:
            retryable = is_retryable(failure)
            _emit(
                log,
                "DEBUG",
                "courier.policy",
                "status={} -> {}".format(
                    failure.status, "retryable" if retryable else "permanent"
                ),
            )
            if not retryable:
                failure.attempts = attempts
                raise
            _emit(
                log,
                "WARN",
                "courier.retry",
                "attempt {}/{} failed ({}), backing off {}s".format(
                    attempts, max_attempts, failure.code, backoff_seconds(attempts)
                ),
            )
    _emit(
        log,
        "ERROR",
        "courier.retry",
        "retry budget exhausted after {} attempts".format(attempts),
    )
    raise RetryBudgetExhausted(destination, attempts)


def _emit(log, level, source, message):
    if log is not None:
        log("{} {} {}".format(level, source, message))
