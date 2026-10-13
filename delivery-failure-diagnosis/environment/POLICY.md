# Delivery retry policy

This document is the specification for how the courier decides whether a failed
delivery attempt is worth repeating. The service is required to conform to it.

## What retryable means

1. A failure is retryable only if the same delivery, unchanged, could succeed
   on a later attempt. Anything that will be rejected identically every time is
   permanent.

## Classifying a failure

2. Status `408` and status `429` are retryable. Every other 4xx status is
   permanent.

3. A 5xx status is retryable **unless** the response body carries a permanent
   failure code.

4. **The failure code takes precedence over the status.** A response may carry
   a retryable status and still describe a permanent condition; the endpoint
   reports transport health in the status and the actual decision in the code.
   The permanent codes are:

   - `destination_disabled`
   - `unknown_destination`
   - `payload_rejected`
   - `signature_invalid`

## Spending the budget

5. The retry budget is **five attempts**. That figure is part of the contract
   with the scheduler, which sizes its dispatch window around it, and is not
   the service's to change.

6. A permanent failure must be attempted **exactly once**. The retry budget
   exists for transient faults. Spending it on a delivery that can never
   succeed delays every other job in the queue behind it, which is the whole
   cost this policy exists to avoid.

7. `permanent_failure` and `retries_exhausted` are different outcomes and must
   stay distinguishable. The queue drops the first and re-enqueues the second.
   A retryable failure that spends the whole budget is reported as
   `retries_exhausted` and never as a permanent failure.

## Reporting

8. The reason reported for a permanent failure is the failure code that caused
   it.

9. The reason reported for `retries_exhausted` is `upstream_unavailable`,
   regardless of which code the final attempt returned. The individual codes
   are already in the log; the outcome describes the delivery, not the last
   packet.
