FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN pip install --no-cache-dir pytest==8.3.3

WORKDIR /app

COPY courier /app/courier
COPY tests /app/tests
COPY POLICY.md /app/POLICY.md
COPY run.log /app/run.log
COPY README.md /app/README.md

RUN mkdir -p /logs/agent /logs/verifier

CMD ["sleep", "infinity"]
