"""Decides whether a failed delivery attempt is worth repeating."""

RETRY_AFTER_STATUSES = (408, 429)


def is_retryable(failure):
    """Return True when the failure may succeed on a later attempt."""
    if failure.status in RETRY_AFTER_STATUSES:
        return True
    if failure.status >= 500:
        return True
    return False
