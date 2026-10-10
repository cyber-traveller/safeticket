# Experiments and history

Material moved out of the front-page README: the early development notes, the policy
versions, and the comparisons with other systems. These are small, authored,
synthetic experiments; none of them is evidence that SafeTicket is better than any other
system. The current results are in the [README](../README.md#results).

## Early status and policy notes

The local model backend and the SafeTicket API are installed. Initial latency samples
are recorded in `benchmarks/results/`; these are preliminary measurements.

SafeTicket now provides `POST /v1/support/decide` with a body such as
`{"ticket":"I was charged twice for the same order."}`. Its support policy
routes sufficiently confident cases and requests human review for uncertain
cases or suspected unauthorized access/payments. The 0.70 route threshold is
an uncalibrated starting point. Review means a recommendation in the response;
no ticket is sent to a person automatically.

Run `.venv/bin/python -m benchmarks.evaluate_support` with Kev on port 8008.
The 16 authored development examples include ambiguity, multiple requests,
incidents, and an injected instruction. Results are in
`outputs/support-evaluation.json`: 11 automatic routes, one routing error,
and five of six review-required cases caught in the first run. This is a
small development smoke test, not a held-out production evaluation or evidence
of improved model weights. No training has been performed. Validate on fresh
customer-labeled data before relying on automatic routing.

### Support policy v2

The live support endpoint now uses `safeticket/support_v2.py`, with separate checks
for multiple unresolved requests and unauthorized activity. The route
threshold is 0.55 with a minimum 0.25 lead over the next option. These settings
are not calibrated on customer data. Whitespace-only input is rejected.
The preceding v1 results and 0.70 threshold are historical.

The policy also contains a narrow billing-document guardrail: explicit receipt,
invoice, and billing-statement requests can be routed to billing when incident
and multiple-request checks are clear. This rule is tested separately and
fails closed when those checks are not valid.

On a fresh 24-ticket synthetic evaluation, correct actions rose from 17 to 19;
incorrect automatic routes remained at two. See
`outputs/safeticket-improvement-report.md` and `outputs/support-v2-holdout.json`.
Reproduce with `.venv/bin/python -m benchmarks.evaluate_v2 --fixture
benchmarks/support_holdout_v2.json --output work/holdout-rerun.json`.
Re-running this now-examined set is regression testing, not a new holdout.

For a paired System One-compatible comparison, set `SYSTEMONE_API_KEY` when
needed and run:

```text
work/laya-env/bin/python -m benchmarks.run_systemone_comparison \
  --base-url https://example.invalid --model jev-latest
```

The runner uses the same support and review fixtures as the local comparisons
and never writes the API key to its output.

To isolate policy changes from model changes, replay the frozen model outputs
with `.venv/bin/python -m benchmarks.replay_support_policy`. This produces
`outputs/support-policy-replay.md`; it is a policy replay, not fresh inference.

## Laya comparison

The isolated environment `work/laya-env` contains Laya 0.4.1; pinned English
and typed-decisions checkpoints are in `work/laya-models`. See
`outputs/laya-comparison-report.md` for the matched quality comparison:
SafeTicket/Kev 24/24, Laya English 17/24, and Laya typed-decisions 15/24 correct
actions as recorded (replaying the current policy on the frozen outputs gives
24/24, 19/24 and 19/24) with the same SafeTicket support policy. These are synthetic,
fixed-prompt results; the prompts were developed on Kev and no general
superiority claim is made.

Reproduce each backend sequentially from the project root:

```text
work/laya-env/bin/python -m benchmarks.run_laya_comparison --backend kev
HF_HUB_OFFLINE=1 work/laya-env/bin/python -m benchmarks.run_laya_comparison --backend english
HF_HUB_OFFLINE=1 work/laya-env/bin/python -m benchmarks.run_laya_comparison --backend typed-decisions
.venv/bin/python -m benchmarks.summarize_laya
```

These commands overwrite the corresponding comparison outputs. The fixture
has now been examined; reruns are regression tests, not a new holdout.

