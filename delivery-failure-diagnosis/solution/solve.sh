#!/bin/bash
# Reference solution.
#
# The retry layer in run.log is doing exactly what it was told to do. The
# defect is one line above every one of those WARN entries:
#
#   INFO  courier.transport attempt=1 destination=dst-2210 -> 503 destination_disabled
#   DEBUG courier.policy    status=503 -> retryable
#
# The transport reported both a status and a code; the classifier considered
# only the status. POLICY rule 4 says the code takes precedence, so a 503
# carrying destination_disabled is permanent and must cost one attempt, not
# five.
#
# This is ONE valid path. The rubric scores the observable outcome and the
# number of calls the endpoint received, not the text of this file.
set -euo pipefail

cat > /app/courier/policy.py <<'PYEOF'
"""Decides whether a failed delivery attempt is worth repeating."""

RETRY_AFTER_STATUSES = (408, 429)

# A response may carry a healthy-looking transport status and still describe a
# condition that will be rejected identically on every future attempt. The code
# is the endpoint's decision; the status only describes transport health.
PERMANENT_CODES = frozenset(
    {
        "destination_disabled",
        "unknown_destination",
        "payload_rejected",
        "signature_invalid",
    }
)


def is_retryable(failure):
    """Return True when the failure may succeed on a later attempt."""
    if failure.code in PERMANENT_CODES:
        return False
    if failure.status in RETRY_AFTER_STATUSES:
        return True
    if failure.status >= 500:
        return True
    return False
PYEOF

cd /app && python -m pytest tests -q
