"""Deterministic stand-in for the delivery endpoint.

No sockets and no clock. Each destination has a scripted sequence of replies;
the last entry repeats once the sequence runs out, so a destination that is
permanently broken stays permanently broken.
"""

OK = "ok"


class Job:
    """One outbound delivery."""

    def __init__(self, job_id, destination, payload=b""):
        self.id = job_id
        self.destination = destination
        self.payload = payload


class Transport:
    """Replays a scripted reply sequence and counts the calls it received."""

    def __init__(self, script):
        self._script = script
        self.attempts = {}

    def send(self, job):
        from courier.failures import DeliveryFailure

        destination = job.destination
        self.attempts[destination] = self.attempts.get(destination, 0) + 1

        replies = self._script.get(destination)
        if not replies:
            raise DeliveryFailure(404, "unknown_destination")

        index = min(self.attempts[destination] - 1, len(replies) - 1)
        reply = replies[index]
        if reply == OK:
            return "receipt-{}".format(job.id)
        status, code = reply
        raise DeliveryFailure(status, code)

    def attempts_for(self, destination):
        return self.attempts.get(destination, 0)


# The reply sequences captured from the failing production run.
DEFAULT_SCRIPT = {
    "dst-2210": [(503, "destination_disabled")],
    "dst-1002": [(404, "unknown_destination")],
    "dst-3001": [(503, "upstream_timeout"), (503, "upstream_timeout"), OK],
    "dst-4004": [(500, "internal_error")],
    "dst-7788": [OK],
}
