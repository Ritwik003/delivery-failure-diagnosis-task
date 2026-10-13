The courier at `/app` overran its dispatch window last night and deferred two
jobs to the next one. `run.log` is the recorded output of that window.

Job `jb-4418`, bound for destination `dst-2210`, finished as
`retries_exhausted (upstream_unavailable)` after spending all five attempts.
The destination team have since confirmed that `dst-2210` was switched off
before the window opened and could not have accepted anything.

`cd /app && python -m pytest tests` reproduces it:
`test_disabled_destination_is_permanent` fails.

Read `run.log`, work out what actually went wrong, and fix it so that every
delivery is classified and reported as `POLICY.md` specifies.

Constraints:

- `POLICY.md` is the specification for this service. Every outcome must
  conform to it. Do not edit `POLICY.md`.
- `run.log` is evidence from a past run. Do not edit it.
- Do not change the public API of `courier.service`: `deliver(job, transport,
  log)` keeps its parameter names, and `Result` keeps its `outcome`, `reason`
  and `attempts` fields with their current meanings.
- Do not delete, skip, rename, or weaken any test in `/app/tests`.
- Do not add third-party dependencies. The service is standard library only.
- Keep the service deterministic. No sleeping, no wall-clock reads, no network.

`cd /app && python -m pytest tests` must pass when you are done.
