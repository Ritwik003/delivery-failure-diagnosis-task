# Task 4 — delivery-failure-diagnosis

A Harbor benchmark task measuring **diagnosing a fault from runtime evidence
rather than from source code alone**.

A courier hands jobs to an endpoint that is allowed to fail, behind a retry
layer with a fixed budget. It ships `run.log`, the recorded output of a
dispatch window that overran. Every loud line in that log comes from the retry
layer doing its job correctly: repeated warnings, widening backoff, and a stack
trace naming the retry module. The defect is one quiet line that classifies
each failure on its transport status while ignoring the permanent code reported
alongside it, so a destination switched off before the window opened is retried
to exhaustion instead of being abandoned at once.

The task is not measuring whether a model can fix a retry loop. It is measuring
whether the model can tell a symptom from a cause when the loudest evidence
points at the wrong component. A fix aimed at the retry layer can turn the whole
visible suite green and still call a dead endpoint five times.

## Requirements

- **Docker**, running
- **Python 3.11 or newer**

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS / Linux

pip install -r requirements.txt
```

`pytest` is not installed here. It runs inside the task container and is pinned
in `environment/Dockerfile`.

## API key

```bash
cp .env.example .env
```

Then open `.env` and fill in `MINIMAX_API_KEY`. Nothing else needs editing; the
fallback variables resolve from that one value. Do not commit `.env`.

## Running

Run the reference solution first. If it does not report `accuracy = 1.0` and
`all_criteria_met = 1.0`, the task is broken rather than the model:

```bash
harbor run -p ./delivery-failure-diagnosis -a oracle
```

Then run a model. Three attempts minimum, since one agentic run is noise:

```bash
harbor run -p ./delivery-failure-diagnosis -a opencode -m minimax/MiniMax-M2.7 --env-file .env -k 3
```

If the `minimax/` provider fails to authenticate, switch to the
OpenAI-compatible route already configured in `.env`:

```bash
harbor run -p . -a opencode -m openai/MiniMax-M2.7 --env-file .env -k 3
```

### If you see "Docker daemon is not running"

Docker probably *is* running. Harbor's preflight check gives the daemon ten
seconds to answer, and a cold Docker Desktop can take longer than that to wake.
Wake it first in the same command:

```bash
docker info > /dev/null; harbor run -p ./delivery-failure-diagnosis -a oracle
```

On Windows PowerShell use `docker info > $null;` instead. Turning off Resource
Saver in Docker Desktop settings stops it recurring.

## Reading the results

The headline accuracy is the least informative number. Each trial writes one
score per criterion:

```bash
cat jobs/<timestamp>/*/verifier/reward.json
```

| Criterion | Meaning |
| --- | --- |
| `root_cause_fixed` | A permanent condition is recognised as permanent, whatever status carried it |
| `attempt_efficiency` | A permanent failure costs exactly one call, and the budget is still spent on genuinely transient faults |
| `spec_conformance` | Policy rules no repository test covers |
| `retry_behaviour_intact` | Preservation. The retry layer still retries and still honours its budget |
| `constraints_respected` | Guardrail. Tests, specification and recorded log untouched |

Read the first three as the capability signal. `attempt_efficiency` is the
one that separates a correct answer from a correct answer arrived at the wrong
way: it counts the calls the endpoint actually received, not the number the
service reports about itself. A fix that retries first and classifies afterwards
scores full marks for correctness and close to nothing here.

`retry_behaviour_intact` exists so that efficiency cannot be bought by refusing
to retry at all. It reads high on an untouched repository and carries no
information until something has changed; read it beside `attempt_efficiency`,
never alone.

`all_criteria_met` is the strict pass rate: every criterion perfect, or zero.

`jobs/<timestamp>/*/verifier/pytest.log` names the exact assertion that failed.
That is the qualitative finding worth reporting.

## Layout

```
README.md                      this file
requirements.txt               host-side dependency
.env.example                   template for .env

delivery-failure-diagnosis/    the task itself
  task.toml                    metadata, timeouts, resources
  instruction.md               the only thing the agent is given
  environment/                 built into the image, becomes /app
    Dockerfile
    courier/                   the delivery service
    tests/                     visible suite
    POLICY.md                  the retry specification
    run.log                    recorded output of the failing dispatch window
  tests/                       hidden; copied to /tests at verify time only
  solution/solve.sh            reference fix, scores full marks on every criterion
```

Every file in `environment/` is copied by the Dockerfile. Removing one, README
included, breaks the image build. `POLICY.md` and `run.log` are not
documentation: they are the evidence the agent is meant to reason from.

The service is fully deterministic. No network, no sleeping, no clock reads and
no random jitter; the endpoint is a scripted fixture that fails predictably.
