# SafeTicket

[![tests](https://github.com/cyber-traveller/safeticket/actions/workflows/tests.yml/badge.svg)](https://github.com/cyber-traveller/safeticket/actions/workflows/tests.yml)

SafeTicket is an open-source, local decision API for support-ticket routing. Its own
work is the safety-focused policy layer (confidence and margin thresholds, and
human-review gates for ambiguity, multiple requests, possible incidents, and
prompt injection), the typed-decision API, and the validation and benchmark
harness with the fixtures used to measure them.

**Model backend:** the live API currently runs the pinned Kev model
(`jaredpalmer/kev-0.8b@v1.0`; the Kev project is Apache-2.0, Copyright 2026 Jared
Palmer) locally on Apple Silicon. SafeTicket has not trained independent weights, and no Kev source code or
model weights are copied into this repository. See "Model backend and
provenance" below, `NOTICE`, and `PROVENANCE.md`.

## Status

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

### Active policy: support-v2

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

### Latest results (2026-10-10)

Live API, safe mode, Kev backend, final policy. All fixtures are authored
synthetic data, not production evidence.

| Fixture | Result | Wrong automatic routes | Required reviews caught |
|---|---:|---:|---:|
| Blind (100) | 99/100 | 0 | 20/20 |
| Expanded (200) | 199/200 | 0 | 40/40 |
| Holdout v2 (24) | 24/24 | 0 | 9/9 |
| Fresh (24) | 24/24 | 0 | 9/9 |
| Adversarial v1 (12) | 12/12 | 0 | 4/4 |
| Challenge v1 (12) | 12/12 | 0 | 4/4 |

- The one miss on the blind and expanded sets is the same ticket (b031, an
  injected instruction); it goes to human review.
- The policy was adjusted after failures on the holdout (h11) and the original
  24-case set (n12, n14, n15), so those sets are now regression tests. The
  original set replays at 24/24 on the frozen Kev outputs.
- The independent Qwen adapter remains shadow-only. Its raw model scores 22/24
  validation and 11/12 test (guarded 24/24 and 12/12) and cannot replace the
  live backend yet.
- Latency on the blind set: about 277 ms median in fast mode, 480-530 ms in
  safe mode. 51 unit tests pass.
- Earlier claims of 200/200 (expanded) and 100/100 (blind) were not
  reproducible.

Reproduce a live run with `SAFETICKET_CHALLENGE_FIXTURE=benchmarks/support_blind_v1.json
.venv/bin/python benchmarks/evaluate_live_blind.py` (SafeTicket on port 8009), and the
gate with `.venv/bin/python benchmarks/summarize_gate.py`. See
`outputs/safeticket-benchmark-gate.md`, `outputs/safeticket-scorecard.md`, and
`safeticket/STATUS.md` for the full evidence.

## Model backend and provenance

- Backend and upstream implementation: [jaredpalmer/kev](https://github.com/jaredpalmer/kev)
- Upstream code license: Apache-2.0
- Upstream model cards: [Kev on Hugging Face](https://huggingface.co/collections/jaredpalmer/kev-6aad9d0ea49f2589665e07cd)
- Upstream model revisions for Kev 1.0 are recorded in `PROVENANCE.md`.
- SafeTicket currently contains original benchmark/harness code only; it does not
  claim original model training or original model weights.

## Setup and running

Setup details are in [`docs/SETUP.md`](docs/SETUP.md): the target baseline, running
the benchmark harness, and starting the SafeTicket API on port 8009 (interactive docs at
`/docs`). The API identifies its model backend in `/v1/models` and in every
response; it is an API and policy layer, not a claim of independent model training.

## Attribution

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

## Upstream attribution

See `NOTICE` and `PROVENANCE.md`. If SafeTicket later incorporates upstream Kev code,
the modified files must carry prominent change notices and the upstream
Apache-2.0 notices must remain with the distributed derivative work.

## License

SafeTicket's own source code, benchmarks, and documentation are licensed under the
Apache License, Version 2.0; see `LICENSE`. The copyright line is in `NOTICE`.

Third-party material keeps its own license and is not relicensed by this
project: the Kev backend (Apache-2.0, Copyright 2026 Jared Palmer) and its model
weights, the Qwen2.5 base models used for the independent-model experiments, and
the BANKING77 dataset (CC BY 4.0), each under its own terms. Model weights and upstream checkouts under
`work/` are not part of this repository. See `NOTICE`, `PROVENANCE.md`,
`safeticket/PROVENANCE.md`, and `benchmarks/BANKING77_PROVENANCE.md`.
