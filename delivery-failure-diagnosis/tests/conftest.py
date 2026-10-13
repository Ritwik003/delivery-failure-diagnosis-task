"""Turns rubric-marked test outcomes into a Harbor reward file.

Each test carries @pytest.mark.rubric("<criterion>"). The verifier emits one
score per criterion plus an overall figure, so a run tells you *which*
requirement the agent missed rather than only that it missed something.
"""

import json
import os

_REWARD_DIR = "/logs/verifier"

_CRITERIA = {}   # nodeid -> criterion
_OUTCOMES = {}   # nodeid -> outcome


def pytest_configure(config):
    config.addinivalue_line("markers", "rubric(name): rubric criterion this test scores")


def pytest_collection_modifyitems(session, config, items):
    for item in items:
        marker = item.get_closest_marker("rubric")
        _CRITERIA[item.nodeid] = marker.args[0] if marker else "uncategorised"


def pytest_runtest_logreport(report):
    if report.when == "call":
        _OUTCOMES[report.nodeid] = report.outcome
    elif report.when in ("setup", "teardown") and report.outcome == "failed":
        _OUTCOMES[report.nodeid] = "failed"


def pytest_sessionfinish(session, exitstatus):
    buckets = {}
    for nodeid, criterion in _CRITERIA.items():
        outcome = _OUTCOMES.get(nodeid, "failed")
        passed, total = buckets.get(criterion, (0, 0))
        buckets[criterion] = (passed + (1 if outcome == "passed" else 0), total + 1)

    payload = {}
    for criterion, (passed, total) in sorted(buckets.items()):
        payload[criterion] = round(passed / total, 4) if total else 0.0

    total_passed = sum(passed for passed, _ in buckets.values())
    total_tests = sum(total for _, total in buckets.values())

    payload["accuracy"] = round(total_passed / total_tests, 4) if total_tests else 0.0
    payload["all_criteria_met"] = 1.0 if total_tests and total_passed == total_tests else 0.0
    payload["passed"] = total_passed
    payload["total"] = total_tests

    os.makedirs(_REWARD_DIR, exist_ok=True)
    with open(os.path.join(_REWARD_DIR, "reward.json"), "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)
    with open(os.path.join(_REWARD_DIR, "reward.txt"), "w", encoding="utf-8") as handle:
        handle.write(str(payload["accuracy"]))
