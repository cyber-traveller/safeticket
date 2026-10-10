# SafeTicket

A cautious, local router for support tickets: it sends a ticket to a team only when the evidence is clearly safe, and otherwise tells you to ask a human.

[![tests](https://github.com/cyber-traveller/safeticket/actions/workflows/tests.yml/badge.svg)](https://github.com/cyber-traveller/safeticket/actions/workflows/tests.yml)
[![License: Apache-2.0](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)

SafeTicket is an open-source, local decision API for support-ticket routing. Its own work is the
safety-focused policy layer (confidence and margin thresholds, and human-review gates for ambiguity,
multiple requests, possible incidents, and prompt injection), the typed-decision API, and the validation
and benchmark harness with the fixtures used to measure them.

**Model backend:** the live API currently runs the pinned Kev model (`jaredpalmer/kev-0.8b@v1.0`; the Kev
project is Apache-2.0, Copyright 2026 Jared Palmer) locally on Apple Silicon. SafeTicket has not trained
independent weights, and no Kev source code or model weights are copied into this repository. See
[Model backend and provenance](#model-backend-and-provenance), `NOTICE`, and `PROVENANCE.md`.

## Highlights

- **Routes or defers.** Each ticket gets either a team (`billing`, `shipping`, `returns`, `access`) or
  `human_review`, with a machine-readable reason.
- **Fails closed.** Ambiguous or close-call tickets, several unresolved requests in one ticket, possible
  account compromise or unauthorized payments (including "I never authorized this"), injected instructions,
  and malformed model output all go to review instead of being routed.
- **Explainable.** Every response carries the model's probabilities, the policy version and thresholds, and
  the reason for the decision.
- **Stable by default.** In `safe` mode the ticket is re-scored with the options in a different order; an
  unstable answer goes to review. `fast` mode skips this check for lower latency.
- **Local.** Tickets are scored on your machine by the backend model; nothing is sent to a third party.
- **Typed-decision pass-through.** `/v1/systemone` forwards typed questions to the backend unchanged.
- **Measured.** A benchmark harness, frozen-output policy replay, and an over-escalation check come with the
  repository, together with the evidence and its limits.

Review means a recommendation in the response. No ticket is sent to a person automatically.

## Quick start

You need Python 3.12 or 3.13 and [uv](https://docs.astral.sh/uv/). The backend model needs Apple Silicon (MLX)
or a supported GPU.

**1. Start the backend model** (see the [Kev README](https://github.com/jaredpalmer/kev) for details):

```bash
git clone https://github.com/jaredpalmer/kev.git && cd kev
uv sync --extra serve
uv run --extra serve python -m kev.serve --run jaredpalmer/kev-0.8b@v1.0 --port 8008
```

**2. Start SafeTicket** in another terminal:

```bash
git clone https://github.com/cyber-traveller/safeticket.git && cd safeticket
uv sync --extra serve
uv run --extra serve uvicorn safeticket.serve:app --host 127.0.0.1 --port 8009
```

**3. Ask for a decision:**

```bash
curl -s localhost:8009/v1/support/decide -H 'content-type: application/json' \
  -d '{"ticket":"I was charged twice for my order."}'
```

Interactive API docs are at <http://127.0.0.1:8009/docs>. More setup detail is in [docs/SETUP.md](docs/SETUP.md).

## API

### `POST /v1/support/decide`

Request: `{"ticket": "<text>"}`. The ticket must be non-empty (whitespace-only is rejected) and at most
16,000 characters. Invalid requests return `422`.

```jsonc
{
  "decision": {
    "action": "route",                       // "route" | "human_review"
    "team": "billing",                       // billing | shipping | returns | access | null
    "reason": "eligibility_and_routing_agree"
  },
  "evidence": { "answers": { "team": {...}, "urgent": {...}, "multiple": {...} }, "safeticket": {...} },
  "robustness": { "enabled": true, "argmax_stable": true, "permutations": 2, ... },
  "policy": { "version": "support-v2", "threshold": 0.55, "minimum_margin": 0.25,
              "calibrated_on_customer_data": false, "mode": "safe" }
}
```

Examples:

| Ticket | Decision | Reason |
|---|---|---|
| "I was charged twice for my order." | route to `billing` | `eligibility_and_routing_agree` |
| "There is a charge on my statement that I never authorized." | `human_review` | `possible_security_or_payment_incident` |
| "I need a new invoice and help recovering my forgotten password." | `human_review` | `multiple_unresolved_requests` |

Common reasons include `eligibility_and_routing_agree`, `clear_billing_document_request`,
`multiple_unresolved_requests`, `possible_security_or_payment_incident`, `low_model_probability`,
`insufficient_or_conflicting_evidence`, `option_order_instability`, and
`instruction_injection_requires_review`.

### Other endpoints

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/`, `/health` | Service status and endpoint list |
| `GET` | `/v1/models` | Model metadata, including the backend that is in use |
| `POST` | `/v1/systemone`, `/v1/systemone/permute`, `/v1/systemone/separate` | Typed-decision pass-through to the backend |
| `POST` | `/v1/support/shadow` | Compare the live decision with the optional independent model |
| `POST` | `/v1/banking/intent` | Experimental banking-intent classifier |

The `GET` form of each decision endpoint returns a short usage description.

### Configuration

| Variable | Default | Effect |
|---|---|---|
| `SAFETICKET_MODE` | `safe` | `safe` re-scores with reordered options and reviews unstable answers; `fast` skips that check |
| `SAFETICKET_BACKEND_URL` | `http://127.0.0.1:8008` | Backend model server |
| `SAFETICKET_BACKEND_TIMEOUT_SECONDS` | `120` | Backend call timeout |
| `SAFETICKET_CONSISTENCY_PERMUTATIONS` | `2` | Option orders tried in `safe` mode (2 to 6) |
| `SAFETICKET_INDEPENDENT_URL` | unset | Optional independent shadow model for `/v1/support/shadow` |
| `SAFETICKET_SHADOW_TIMEOUT_SECONDS` | `30` | Shadow call timeout |

## How it works

1. **The backend answers three typed questions** about the ticket: which team it belongs to (probabilities
   over billing, shipping, returns, access, or review), whether it looks urgent or like an incident, and
   whether it contains several unresolved requests.
2. **The policy (`safeticket/support_v2.py`) decides** with ordered checks. It routes only when the top team
   has probability of at least 0.55 and leads the next option by at least 0.25. Otherwise it asks for review.
3. **Deterministic text rules cover what a small model misses:** negated authorization ("never authorized",
   "without my permission"), changes to an account by someone else, explicit receipt or invoice requests,
   mixed requests, and instruction-like text inside a ticket, which is treated as untrusted content.
4. **Safe mode re-scores the ticket** with the options in different orders. If the winning team changes, the
   ticket goes to review.
5. **An optional independent model** (a small LoRA adapter on a Qwen base) runs in shadow mode for
   comparison. It never makes live decisions: its raw output does not yet meet the promotion gate.

## Results

Live API, safe mode, Kev backend, final policy (2026-10-10). Every fixture is authored synthetic data, not
production evidence.

| Fixture | Result | Wrong automatic routes | Required reviews caught |
|---|---:|---:|---:|
| Blind (100) | 99/100 | 0 | 20/20 |
| Expanded (200) | 199/200 | 0 | 40/40 |
| Holdout v2 (24) | 24/24 | 0 | 9/9 |
| Fresh (24) | 24/24 | 0 | 9/9 |
| Adversarial v1 (12) | 12/12 | 0 | 4/4 |
| Challenge v1 (12) | 12/12 | 0 | 4/4 |

- The one miss on the blind and expanded sets is the same ticket (b031, an injected instruction). It goes to
  human review, the safe direction.
- On 44 plain single-intent tickets written for an over-escalation check, 38 were routed to the right team,
  6 were sent to review unnecessarily, and none went to a wrong team. Six tickets that genuinely need review
  were all caught.
- Latency on the blind set: about 277 ms median in `fast` mode and 480 to 530 ms in `safe` mode.
- The independent adapter remains shadow-only. Its raw model scores 22/24 on validation and 11/12 on test
  (24/24 and 12/12 with the guard) and cannot replace the live backend yet.

**How to read these numbers.** The policy was adjusted after failures on several of these sets, so those are
now regression tests rather than untouched tests. Earlier claims of 200/200 and 100/100 could not be
reproduced and were corrected. The numbers show that the safety gates behave as designed on the authored
cases; they do not show production accuracy and they are not a comparison against other systems. The
full evidence is in `outputs/safeticket-scorecard.md`, `outputs/safeticket-benchmark-gate.md`, and
`safeticket/STATUS.md`.

## Limitations

- **Synthetic evidence only.** The fixtures were written by the policy's author and the thresholds are not
  calibrated on customer data. Validate on fresh, independently labelled tickets before relying on automatic
  routing. A neutral labelled set is not finished.
- **No independently trained model.** Decisions depend on the Kev 0.8B backend. SafeTicket's contribution is the
  policy, the safeguards, and the harness.
- **Keyword rules have blind spots.** Several safeguards are text patterns. Other ways of saying "I didn't
  authorize this" can be missed, and some plain tickets are sent to review unnecessarily (6 of 44 in the
  check above).
- **No head-to-head claim.** Comparisons with other systems in [docs/EXPERIMENTS.md](docs/EXPERIMENTS.md) ran
  under SafeTicket's own policy on small authored sets and favour its setup. They do not show that it is better.
- **English only, small taxonomy.** Four teams plus review. The banking classifier is experimental.
- **Latency.** Safe mode adds roughly 200 ms to each decision, and answers take hundreds of milliseconds on a Mac.

## Development

```bash
python -m unittest tests/test_*.py        # 51 unit tests; no model server needed
```

Benchmarks need the backend and SafeTicket running (see Quick start):

```bash
SAFETICKET_CHALLENGE_FIXTURE=benchmarks/support_blind_v1.json \
  python benchmarks/evaluate_live_blind.py                       # live run on a fixture
python benchmarks/replay_support_policy.py                       # replay frozen model outputs through the policy
python benchmarks/evaluate_overescalation.py                     # unnecessary-review check
python benchmarks/summarize_gate.py                              # regenerate the benchmark gate
```

| Path | Contents |
|---|---|
| `safeticket/` | API (`serve.py`), policy (`support_v2.py`), safety guard, client |
| `benchmarks/` | Fixtures, evaluation scripts, and recorded baseline results |
| `tests/` | Unit tests |
| `outputs/` | Recorded evaluation results, the scorecard, and the benchmark gate |
| `work/safeticket-independent/` | Scripts and data for the shadow-only independent model |
| `docs/` | Setup guide, experiments and history |

<details>
<summary>Experiments, history, and setup notes</summary>

- [docs/EXPERIMENTS.md](docs/EXPERIMENTS.md): early development notes, earlier policy versions, and the
  comparisons with other systems.
- [docs/SETUP.md](docs/SETUP.md): the target baseline, running the benchmark harness, and starting the API.
- `safeticket/STATUS.md`: the detailed evidence log. `SAFETICKET_PROGRESS.md` and
  `SAFETICKET_RELEASE_CANDIDATE.md`: progress and release status.

</details>

## Model backend and provenance

- Backend and upstream implementation: [jaredpalmer/kev](https://github.com/jaredpalmer/kev)
- Upstream code license: Apache-2.0
- Upstream model cards: [Kev on Hugging Face](https://huggingface.co/collections/jaredpalmer/kev-6aad9d0ea49f2589665e07cd)
- Upstream model revisions for Kev 1.0 are recorded in `PROVENANCE.md`.
- SafeTicket currently contains original benchmark/harness code only; it does not
  claim original model training or original model weights.

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
