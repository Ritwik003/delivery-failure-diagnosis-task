"""Repository test suite for the courier."""

from courier.service import deliver
from courier.transport import DEFAULT_SCRIPT, Job, Transport


def _deliver(job_id, destination):
    return deliver(Job(job_id, destination), transport=Transport(DEFAULT_SCRIPT))


def test_healthy_destination_delivers():
    result = _deliver("jb-1", "dst-7788")
    assert result.outcome == "delivered"


def test_transient_failure_eventually_succeeds():
    result = _deliver("jb-2", "dst-3001")
    assert result.outcome == "delivered"
    assert result.attempts == 3


def test_unknown_destination_is_permanent():
    result = _deliver("jb-3", "dst-1002")
    assert result.outcome == "permanent_failure"
    assert result.reason == "unknown_destination"


def test_disabled_destination_is_permanent():
    result = _deliver("jb-4", "dst-2210")
    assert result.outcome == "permanent_failure"
    assert result.reason == "destination_disabled"


def test_persistent_server_error_exhausts_budget():
    result = _deliver("jb-5", "dst-4004")
    assert result.outcome == "retries_exhausted"
