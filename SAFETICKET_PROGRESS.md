# SafeTicket Project Progress Report

Updated: 2026-10-10

## Project goal

SafeTicket is an open-source decision engine intended to make cautious, typed
support decisions locally. The project began by studying the
public Kev repository and its API shape, while preserving required attribution
and avoiding unsupported claims of original model training.

## Repository and licensing work

- Inspected the Kev repository, installation shape, API routes, model metadata,
  and Apple Silicon compatibility.
- Confirmed that the initial live SafeTicket implementation is a facade over the
  `jaredpalmer/kev-0.8b@v1.0` backend.
- Preserved Kev provenance in API responses and project documentation.
- Kept independent model experiments isolated under `work/safeticket-independent/`.
- Did not publish model weights or claim that the live model was trained from
  scratch.
- Downloaded Qwen2.5-1.5B-Instruct for an isolated experiment. Its official
  model card is available at
  https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct and identifies the model as
  Apache-2.0.

## Local API

SafeTicket runs locally on port 8009:

- `GET /` — service status and endpoint list
- `GET /health` — health check
- `GET /docs` — interactive OpenAPI documentation
- `GET /v1/models` — model metadata
- `POST /v1/systemone` — typed decision facade
- `POST /v1/support/decide` — guarded support routing
- `POST /v1/support/shadow` — live-versus-independent comparison

The root and health endpoints were added and verified after browser requests
returned `Not Found`. The API correctly requires `POST` for decision routes.
Malformed tickets return HTTP 422.

## SafeTicket policy improvements

The support policy was separated into evidence validation, eligibility checks,
team selection, and deterministic safety rules. It now handles:

- Invalid or malformed evidence with fail-closed human review.
- Low-confidence and close-probability decisions with human review.
- Multiple unresolved requests needing different teams.
- Explicit account compromise and unauthorized-payment signals.
- Ordinary forgotten-password and login-lockout requests without falsely
  treating them as security incidents.
- Instruction-injection text as untrusted ticket content.
- High-precision billing requests such as invoices and receipts.
- Shipping, tracking, delivery, exchange, return, and account-access wording.
- Resolved account problems followed by a remaining delivery request.
- Fraud-negation wording such as “this is not fraud.”
- Additional paraphrases such as sorting-center tracking, size exchanges, and
  lost-phone login recovery.

The independent guard additionally handles multi-request escalation,
account-compromise escalation, and injection filtering for billing, shipping,
returns, and access.

## Independent model experiments

### Qwen2.5-0.5B

- Trained an isolated LoRA adapter from authored SafeTicket support examples.
- Evaluated raw and guarded versions on reserved validation and adversarial
  fixtures.
- The raw model was weaker on injection-heavy cases.
- The deterministic guard improved the reserved fixtures but remained
  shadow-only.

### Qwen2.5-1.5B v0.2

- Downloaded the Apache-2.0 base model.
- Trained a controlled adapter using the proven 74-example recipe.
- Raw result: 21/24 validation and 12/12 adversarial.
- Guarded result: 24/24 validation and 12/12 adversarial.
- Fresh challenge: 12/12 guarded.
- This remains the selected independent shadow candidate.

### Rejected adapters

- A larger v0.3-safety adapter trained on 82 examples scored 94/100 raw and
  99/100 guarded on the untouched 100-case sample.
- A one-epoch v0.4-safety adapter scored 90/100 raw and 97/100 guarded.
- Both were rejected, disconnected, and documented as regressions. On the
  smaller validation/test splits they still score well (v0.3-safety: 23/24 raw
  validation, 24/24 guarded), so those splits do not expose the regression the
  100-case sample does.
- The experiments showed that small targeted fine-tuning runs can overfit and
  damage generalization.

## Benchmark results

### Authored support fixtures

- Frozen support comparison: SafeTicket 18/24 versus Kev 17/24.
- Jev comparison: SafeTicket 24/24 versus Jev 20/24 (recorded earlier; the current policy still replays SafeTicket/Kev at 24/24).
- Laya comparison: SafeTicket policy 21/24 versus Laya English 17/24 and typed
  decisions 15/24.
- Open Alternative support challenge: SafeTicket 12/12 versus 3/12.
- Expanded live policy fixture: 199/200 (re-run 2026-10-10), with 0 automatic-route errors and
  40/40 required reviews caught. Miss b031 goes to human review (safe direction).
- Independent 100-case comparison:
  - Live SafeTicket: 100/100 as recorded; 99/100 on the 2026-10-10 re-run (b031 goes to
    human review, 0 automatic errors).
  - Raw independent v0.2: 96/100.
  - Guarded independent v0.2: 100/100.
- Median latency on the 100-case comparison was approximately 138 ms for live
  SafeTicket and 269 ms for the shadow path; shadow p95 was approximately 359 ms. A
  2026-10-10 re-run with four concurrent workers measured about 492 ms and
  901 ms median, which is not comparable with those figures.
- Regression suite currently passes 58/58 tests.

These fixtures are authored synthetic cases. They demonstrate tested behavior,
not universal model superiority or production accuracy.

### External BANKING77 diagnostic

The official BANKING77 test split was downloaded with provenance metadata. The
dataset contains 77 fine-grained banking intents and is distributed under CC
BY 4.0. See `benchmarks/BANKING77_PROVENANCE.md`.

Under a local, coarse mapping from those 77 intents to SafeTicket’s five teams:

- Live SafeTicket: 28/77.
- Independent model: 45/77.

This is a domain-coverage diagnostic, not a fair leaderboard. Many BANKING77
intents do not map cleanly to billing, shipping, returns, access, or review.
The separate training split is being used only for development; the official
test split remains untouched by tuning.

## Re-verification, 2026-10-10

The live benchmarks and the independent adapter evaluations were re-run. Details
are in `safeticket/STATUS.md`.

- A first re-run found the holdout at 23/24 with one wrong automatic route (h11,
  an invoice request combined with password recovery). A rule now sends a billing
  document request combined with an access request to human review, except when
  the access issue is stated as solved.
- Replaying the policy on the original 24-case set showed three more wrong
  automatic routes (n12, n14, n15; n15 was a possible account takeover). The
  incident check now catches third-party account changes, and the two-request
  checks recognise more action verbs. These rules were written after seeing the
  failures, so that set is no longer an untouched test.
- Final live results (safe mode, zero automatic-route errors on all): blind
  99/100, expanded 199/200, holdout 24/24, fresh 24/24, adversarial 12/12,
  challenge 12/12. The one miss on blind and expanded is b031, which goes to
  human review.
- Latency on the blind fixture: fast about 277 ms median, safe about 480-530 ms.
- The independent adapter results reproduce the recorded files. All seven adapter
  versions are tabulated in `safeticket/STATUS.md` and `outputs/safeticket-benchmark-gate.md`.
- The earlier 200/200 expanded and 100/100 blind claims were not reproducible.

## Current architecture and status

- Live `/v1/support/decide` remains Kev-backed.
- The independent Qwen2.5-1.5B v0.2 adapter is shadow-only.
- The guarded shadow path currently matches live SafeTicket on the bounded 100-case
  support comparison.
- The raw independent model is not yet ready to replace the live backend.
- The source repository is public on GitHub (`cyber-traveller/safeticket`, 2026-10-10).
  A model release has not been authorized or performed.
- The current promotion gate allows the live policy and guarded shadow path,
  but blocks raw-model replacement.

## Important limitations

- Most comparisons use small authored synthetic fixtures.
- The support policy and many fixtures were developed around Kev, so the
  comparisons are not fully neutral model benchmarks.
- The live system is not an independently trained model yet.
- The BANKING77 coarse mapping is an explicit local assumption.
- No claim is made that SafeTicket is universally better than Kev, Jev, Laya, or other
  systems.

## Key files

- `safeticket/serve.py` — local API and endpoint definitions.
- `safeticket/support_v2.py` — live support policy.
- `safeticket/independent_guard.py` — independent shadow safety guard.
- `safeticket/STATUS.md` — detailed chronological status and evidence log.
- `benchmarks/` — fixtures and evaluation scripts.
- `outputs/safeticket-scorecard.md` — consolidated comparison scorecard.
- `outputs/shadow-sample-v2.json` — 100-case live/shadow comparison.
- `outputs/banking77-external-v1.json` — external diagnostic report.
- `SAFETICKET_TAXONOMY.md` — proposed broader domain-aware taxonomy, not yet live.
- `safeticket/banking_taxonomy.py` — experimental domain-aware banking classifier.
- `benchmarks/evaluate_banking_taxonomy.py` — development and untouched-test
  taxonomy evaluation.
- `work/safeticket-independent/` — isolated training scripts, data, and adapters.

## Next steps

1. Design a broader, domain-aware SafeTicket taxonomy using the BANKING77 training
   split without touching its official test split.
2. Add independently reviewed labels for a neutral cross-domain benchmark.
3. Improve the raw independent model with a larger, diverse dataset and a
   proper train/validation/test split.
4. Measure Apple Silicon memory, throughput, and cold-start behavior.
5. Re-run the promotion gate before changing the live backend.
6. Ask explicitly before any model release or other major external release.

The experimental banking taxonomy now includes a backward-compatible
`legacy_team` field. After conservative wording and policy-coverage fixes, the
latest run scores 136/154 (88.3%) on the development sample and 76/77 (98.7%)
on the untouched BANKING77 test split. These are taxonomy diagnostics, not
claims of general model superiority.
