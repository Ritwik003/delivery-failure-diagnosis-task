#!/bin/bash
# Harbor verifier entrypoint. conftest.py writes the per-criterion reward file.
# Never exits non-zero on test failure: a failing agent is a valid outcome.
set -u
mkdir -p /logs/verifier

cd /app && python -m pytest /tests/test_rubric.py \
    -p no:cacheprovider -rA -q \
    > /logs/verifier/pytest.log 2>&1

echo "pytest exit code: $?" >> /logs/verifier/pytest.log

if [ ! -f /logs/verifier/reward.json ]; then
    echo '{"accuracy": 0.0, "all_criteria_met": 0.0, "passed": 0, "total": 0}' > /logs/verifier/reward.json
    echo 0 > /logs/verifier/reward.txt
fi

cat /logs/verifier/reward.json
exit 0
