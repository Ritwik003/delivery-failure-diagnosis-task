# courier

Outbound delivery service. Jobs are handed to an endpoint that is allowed to
fail; the courier decides whether a failure is worth repeating.

- `courier/service.py` — the public API: `deliver(job)` returns a `Result`.
- `courier/retry.py` — the retry loop and its budget. Backoff is computed and
  reported but never slept on; the scheduler owns the wall clock.
- `courier/policy.py` — classifies a failed attempt.
- `courier/transport.py` — deterministic stand-in for the endpoint, driven by a
  scripted reply sequence. It counts the calls it receives.
- `courier/failures.py` — the failure types.

`POLICY.md` is the specification the service is required to conform to.

`run.log` is the recorded output of the production dispatch window that
prompted the current investigation.

Run the suite with:

    cd /app && python -m pytest tests
