# SafeTicket completion status

Updated 2026-10-10.

## Complete locally

- SafeTicket-branded TypeSafe-compatible API facade.
- Support decision policy with uncertainty, incident, and multiple-request review gates.
- Conservative billing-document adjudication for explicit receipt and invoice requests.
- Input validation and fail-closed malformed-evidence handling.
- 51 automated tests passing.
- Frozen-output policy replay and matched Kev/Laya benchmark artifacts.
- Kev attribution, provenance, and non-original-training disclosure.

## Not complete yet

- SafeTicket does not have independent model weights; it currently uses the pinned Kev backend.
- jevos has been evaluated on the same fixtures; its one-thread compatibility
  configuration scored 20/24 support actions and 14/18 review cases.
- The current quality fixtures are synthetic and are not production evidence.
- The source repository is public on GitHub (`cyber-traveller/safeticket`, 2026-10-10).
  No model weights or model release have been published.
- Alternative open-source implementations are isolated under `work/alternatives/`
  and audited in `safeticket/ALTERNATIVE_AUDIT.md`.
- Option-order robustness audit: 0 unstable cases across 24 support tickets;
  largest probability spread 0.123 with two permutations.
- Updated support-v2 policy now scores 24/24 on both the fresh fixture and the
  frozen holdout, with zero automatic errors and all required reviews caught.
- Adversarial v1 fixture scores 12/12, with zero automatic errors and all
  review-required cases caught. This remains authored test data, not an
  independent benchmark.
- The live API was rerun on the 24-case fresh support suite after the latest
  fix: 24/24 correct, 0 automatic-route errors, 9/9 required reviews caught,
  and all 5 validation checks passed. Median observed latency was 133 ms in
  that local run.
- The consolidated benchmark gate is recorded in
  `outputs/safeticket-benchmark-gate.json` and `outputs/safeticket-benchmark-gate.md`.
  It passes the current live-policy safety gate and blocks replacing the live
  path with the independent adapter until that adapter reaches 24/24
  validation and 12/12 adversarial accuracy.

## Release gate

SafeTicket should not be described as better than Kev or Jev until a fresh, paired run
shows higher accuracy on a frozen, independently labeled fixture without a
higher unsafe-automatic-route rate. The current policy replay is not that gate.

## Fresh local benchmark

The pinned Kev checkpoint has now been restored and the fresh comparison was
rerun. SafeTicket/Kev scored 24/24 support actions with zero automatic errors; the
review task scored 17/18 cases and 53/54 individual judgments. These remain
synthetic, fixed-prompt results.

The local jevos comparison scored 20/24 support actions with 3 automatic
errors; review comprehension was 14/18 cases and 50/54 individual judgments.
Its default launch also hit an Apple Silicon Xbyak runtime error and required
one thread, a 4096-token context, and disabled dynamic quantization.

The downloaded 0.5B Open Alternative checkpoint passed a local CPU smoke test
with typed probabilities and choices. Its larger published benchmark model was
not downloaded because it is unsuitable for the 16GB target.

The latest policy changes cover ordinary password lockouts, explicit multiple
requests, instruction-injection text, receipt intent, and tickets where an
access issue is already resolved. These are policy improvements, not new model
weights.

## Independent model prototype

An isolated Qwen2.5-0.5B-Instruct LoRA adapter was trained from 74 authored
SafeTicket support examples. The base model is Apache-2.0 and the adapter is stored
under `work/safeticket-independent/`; no Kev predictions were used as labels.

After balancing the labels, increasing LoRA capacity, and training for three
epochs with the prompt masked, the selected adapter scores 11/12 on the
reserved adversarial set and 22/24 on the reserved validation set. A longer
five-epoch run overfit and was rejected. The selected adapter remains below the
live SafeTicket policy layer and is not loaded by the API. Its label-logit calibration
prototype lowers validation Brier score from 0.0902 to 0.0882 with a fitted
temperature of 0.70; this is diagnostic only and is not yet an API default.

The independent adapter is now available in shadow mode at
`POST /v1/support/shadow`. It returns the live policy decision, the independent
model decision, and an agreement flag without changing
`/v1/support/decide` behavior.

The raw independent adapter missed three injection-heavy cases across the
reserved validation/adversarial fixtures. A targeted v0.2 retraining attempt
regressed to 18/24 validation and 10/12 adversarial, so it was rejected and
not promoted. Instead, the shadow path now has a narrow deterministic safety
guard for untrusted instruction text and account-compromise signals. The
guarded shadow path scores 24/24 validation and 12/12 adversarial on the same
fixtures. This is a hybrid guardrail result, not proof that the raw model is
better, and it remains shadow-only.

A larger 89-example, lower-learning-rate v0.3 experiment was also evaluated;
it regressed further to 13/24 validation and 8/12 adversarial, so it was
rejected as well. The original v0.1 adapter and its guarded shadow path remain
the selected versions.

The Apache-2.0 Qwen2.5-1.5B-Instruct checkpoint was downloaded and trained as
another independent experiment. Its raw adapter scored 18/24 validation and
8/12 adversarial; with the existing guard it reached 21/24 and 9/12. It was
rejected and is not connected to the API. A controlled run using the proven
74-example recipe reached 21/24 raw validation, 12/12 raw adversarial, and
24/24 plus 12/12 with the guard. It also scored 12/12 on the fresh challenge,
so it is now the isolated shadow candidate on port 8019; `/v1/support/decide`
is unchanged. The checkpoint provenance is the official [Qwen model
card](https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct).

A separate 12-case challenge set was then evaluated without retraining: the
live SafeTicket path scored 12/12, the raw independent model 10/12, and the guarded
independent path 12/12. The result is recorded in
`outputs/shadow-challenge-v1.json`; it is still synthetic evidence only.

## Next authorized step

The small Open Alternative to Jev checkpoint smoke test passed on the local
CPU path: four typed decisions from one forward pass in about 1.9 seconds.
The result is recorded in `outputs/open-alternative-smoke.json`. It remains an
isolated comparator and is not connected to the live API. On the separate
12-case support challenge it scored only 3/12, so it is not a candidate for
SafeTicket support routing without additional task-specific work. The comparison is
recorded in `outputs/open-alternative-support-challenge.json`. Continue only
with test-backed changes; this does not authorize publishing.

## Blind holdout verification

The authored blind fixture `benchmarks/support_blind_v1.json` contains 100
held-out synthetic support tickets and was not used for training. The latest
live SafeTicket policy run at that time scored 100/100, with 80/80 automatic routes correct, zero
automatic-route errors, and all 20/20 review-required cases caught. This is a
strong result for this fixture, not evidence of universal superiority or a
production benchmark. (The 2026-10-10 re-run on the final policy scores 99/100 with 79/79
automatic routes correct; b031 goes to human review.) The full regression suite also
passed 31 tests at that time.

The independent Qwen2.5-1.5B adapter remains shadow-only. It has not replaced
the Kev-backed live path, and no claim is made that SafeTicket beats Kev, Jev, or Laya
in general without broader, independently labeled evaluations.

The follow-up category verification also scored 24/24, with 0 automatic-route
errors, 9/9 required reviews caught, and 5/5 malformed-input checks passing.
The policy now fail-closes on additional account-compromise wording, respects
explicit fraud negation, and keeps a single return request from being confused
with an instruction-injection phrase.

## Expanded evaluation

An expanded authored fixture now contains 200 labeled synthetic cases: 40 per
team, including paraphrases and adversarial instruction text. The live SafeTicket
policy scored 199/200 on the 2026-10-10 re-run, with 159/159 automatic routes correct, zero automatic
route errors, and 40/40 review cases caught. The one miss (b031, a prompt-injection shipping
ticket) is sent to human review, the safe direction. This remains a controlled policy
evaluation, not customer data or proof of general superiority. The full
live-versus-shadow comparison on all 200 cases was not used as a claim because
the independent 1.5B shadow service is too slow under concurrent load; the
independent model remains shadow-only until a bounded, reproducible comparison
is completed.

## Bounded independent comparison

A fixed 40-case stratified sample from the expanded fixture was evaluated
sequentially against the live and independent paths. Live SafeTicket scored 40/40;
the independent raw model scored 38/40; and the guarded independent path now
also scores 40/40. Median request latency was approximately 137 ms for live
SafeTicket and 270 ms for the shadow path; shadow p95 latency was approximately 401
ms. The improvement came from deterministic handling of multi-request and
account-compromise signals, not new model training. Results are recorded in
`outputs/shadow-sample-v1.json`; this is a small synthetic sample, not proof of
general superiority.

## 100-case shadow comparison

A fixed 100-case stratified sample, with 20 cases per team, was evaluated
sequentially. Live SafeTicket scored 100/100 as recorded (99/100 on the 2026-10-10 re-run; same fixture as the blind set); the independent raw model scored 96/100;
and the guarded independent model scored 100/100. Median latency was
approximately 138 ms for live SafeTicket and 269 ms for the shadow path; shadow p95
latency was approximately 359 ms. The remaining raw-model misses are an
injection-heavy billing case, a multi-request case, and two account-security
cases; the deterministic guard catches all four. The new access-priority guard
and tests are recorded in the codebase. Results are recorded in
`outputs/shadow-sample-v2.json` and remain synthetic evidence only.

## Rejected raw-model improvement

An isolated v0.3-safety adapter was trained from the original 74 examples plus
8 new paraphrased safety examples. On the untouched 100-case sample it scored
94/100 raw and 99/100 guarded, regressing from the selected v0.2 adapter's
96/100 raw and 100/100 guarded result. It is rejected and is not connected to
the shadow service; v0.2 remains the selected candidate. This confirms that
adding a few targeted examples can overfit or disturb unrelated routing, so no
promotion claim is made.

A one-epoch v0.4-safety adapter using the same 82-example data was also
tested. It scored 90/100 raw and 97/100 guarded on the untouched 100-case
sample, so it was rejected and disconnected. v0.2 remains restored as the
shadow candidate. These controlled runs indicate that the current guardrail
layer generalizes better than these small fine-tuning attempts; a future raw
model improvement needs substantially more diverse training data and a proper
validation split.

The consolidated evidence scorecard is saved in `outputs/safeticket-scorecard.md`.
It separates measured support-routing results from claims that remain unproven;
the live API still uses the Kev backend and model publication remains unauthorized.

## External BANKING77 diagnostic

The official BANKING77 test split was downloaded with attribution metadata and
evaluated one case per intent. Under the explicit local mapping from 77 fine-
grained banking intents to SafeTicket's five coarse teams, live SafeTicket scored 28/77 and
the independent path scored 45/77. This is not a fair model leaderboard: the
mapping is ours, many banking intents do not correspond cleanly to SafeTicket teams,
and the independent model is optimized for this kind of short intent text.
The result is useful evidence that SafeTicket needs a broader domain taxonomy before
claiming general decision superiority. Provenance is in
`benchmarks/BANKING77_PROVENANCE.md` and the raw report is in
`outputs/banking77-external-v1.json`.

The separate BANKING77 training split is now available for development only,
with a two-example-per-intent sample in `benchmarks/banking77_dev_v1.json`.
Live SafeTicket scored 55/154 on that development sample under the same coarse team
mapping, with 6 automatic-route errors and 46/48 review cases caught. This
confirms that expanding SafeTicket beyond the current support taxonomy is the next
engineering task; the official test split remains untouched by tuning.

An additive experimental endpoint, `POST /v1/banking/intent`, now provides a
domain-aware baseline for transfers, top-ups, payments, cash, refunds, card
lifecycle, identity/access, security, account policy, and review. It is
explicitly marked experimental and `trained_model: false`; the existing
five-team support endpoint is unchanged. The endpoint has unit coverage and
was manually verified on transfer and account-compromise examples.

The taxonomy evaluator initially compared fine-grained domains directly with
the old five teams; that measurement was corrected by adding an explicit
backward-compatible `legacy_team` field. After broad rule fixes for card
delivery and usage, security wording, top-ups, exchange rates, and banking
phrasing, the domain-aware baseline improved from 44/77 to 53/77 on the
untouched BANKING77 test split and from 92/154 to 100/154 on development. The
existing support endpoint remains unchanged. The current test suite passes
39/39.

Additional development-only fixes for card delivery, contactless and card
troubleshooting, automatic top-ups, exchange wording, and banking phrasing
improved the development sample to 107/154. A second pass added generalized
coverage for card activation and expiry, physical-card ordering, mobile-wallet
policy, ATM and country policy, deposit-balance updates, top-up status, and
identity wording. The latest measured results are 136/154 (88.3%) on
development and 76/77 (98.7%) on the untouched test split. The full suite
passes 47/47. SafeTicket retains its own branding and architecture, while required
source and dataset attribution remains visible; provenance is not concealed.

The latest 12-case promotion challenge was rerun after the confirmed-payment
resolution rule: live SafeTicket scored 12/12, the raw independent adapter scored
11/12, and the guarded independent path scored 12/12. The independent path
remains shadow-only because the raw adapter still misses one challenge case.

Post-change blind validation on the 100-case support fixture scored 99/100,
with 79 automatic routes and zero automatic-route errors; all 20 required
reviews were caught. The full regression suite now passes 51/51.

## Re-verification, 2026-10-10

The live benchmarks were re-run against the running API (safe mode, Kev backend).
Before any change, the holdout scored 23/24 with one wrong automatic route:
h11 ("new invoice ... and help recovering my forgotten password") was routed to
billing. It had previously passed only because the urgency score tripped the
incident gate; a later password-exemption edit removed that accident, and no
other gate catches billing-plus-access tickets.

Fix: `billing_plus_access` rule in `safeticket/support_v2.py` sends a billing-document
request combined with a password/sign-in/recovery request to human review
(`multiple_unresolved_requests`).

Results after the fix (server restarted on the patched code):

| Fixture | Result | Automatic-route errors | Reviews caught |
|---|---:|---:|---:|
| Blind (100) | 99/100 | 0 | 20/20 |
| Expanded (200) | 199/200 | 0 | 40/40 |
| Holdout v2 (24) | 24/24 | 0 | 9/9 |
| Fresh (24) | 24/24 | 0 | 9/9 |
| Adversarial v1 (12) | 12/12 | 0 | 4/4 |
| Challenge v1 (12) | 12/12 | 0 | 4/4 |

Latency on the 100-case blind fixture (4 concurrent workers, local run):

| Mode | Result | Median | p95 | Max |
|---|---:|---:|---:|---:|
| fast (`SAFETICKET_MODE=fast`) | 99/100 | 277 ms | 284 ms | 546 ms |
| consistency (`SAFETICKET_CONSISTENCY_CHECK=1`, resolves to safe) | 99/100 | 477 ms | 538 ms | 550 ms |
| safe (`SAFETICKET_MODE=safe`) | 99/100 | 528 ms | 542 ms | 560 ms |

Measured on the final policy (after the n12/n14/n15 fixes).

The robustness check costs roughly 200-250 ms and did not change any decision on
this fixture. The cause of the occasional slow fast-mode request was not
investigated.

Original 24-case comparison set (n01-n24). Replaying the policy on the frozen
Kev outputs (`benchmarks/replay_support_policy.py`) first scored 21/24, with 3
automatic-route errors, rather than the 24/24 recorded in earlier docs. The live
API gave the same decisions. The failing cases were:

- n12 (undelivered item plus invoice tax correction) routed to billing.
- n14 (missing shipment plus wrong-color return) routed to shipping.
- n15 ("Someone I do not know has changed my account password") routed to access,
  a possible account takeover.

All three are now fixed in `safeticket/support_v2.py`: third-party account changes
("someone ... changed/accessed/reset") count as an incident, and the two-request
checks recognise more action verbs (trace, find, take back, send back, correct).
The replay is back to 24/24 with 0 automatic errors and 9/9 reviews caught for
SafeTicket/Kev; Laya English and typed-decisions replay at 19/24 each. An intermediate
h11 fix also broke n18 ("The login issue is solved ... issue my receipt"); the
billing-plus-access rule now skips tickets that say the issue is solved/resolved/fixed.
The rules were written after seeing these failures, so the n-set is no longer an
untouched test. All six live fixtures were re-run after the final change with
unchanged results.

Independent adapter re-run (2026-10-10). The gate's adapter (Qwen2.5-0.5B LoRA v0.1)
was re-evaluated with `work/safeticket-independent/scripts/evaluate_adapter.py`: validation
22/24 raw and 24/24 guarded, test 11/12 raw and 12/12 guarded. Per-case predictions
are identical to the recorded files. The running shadow server (Qwen2.5-1.5B LoRA
v0.2 plus guard) was compared with the live policy through
`benchmarks/evaluate_shadow_challenge.py`:

| Fixture | Live | Raw independent | Guarded independent |
|---|---:|---:|---:|
| Blind / 100-case comparison | 99/100 | 96/100 | 100/100 |
| Holdout v2 (24) | 24/24 | 21/24 | 24/24 |
| Adversarial v1 (12) | 12/12 | 12/12 | 12/12 |
| Challenge v1 (12) | 12/12 | 11/12 | 12/12 |

The only case where guarded independent beats live is b031, which live sends to
review. Latency in this run (4 concurrent workers calling both services) was
about 492 ms median for live and 901 ms median / 1388 ms p95 for the shadow path.
That is much slower than the 269 ms recorded earlier, so it should not be quoted
as shadow latency. The gate decision is unchanged: the raw adapter is not ready to
replace the live path; the guarded path remains shadow-only.

Raw re-run outputs: `outputs/independent-rerun-2026-10-10/`.

All adapter versions re-evaluated (2026-10-10) with `evaluate_adapter.py`, using each
adapter's own base model, on the validation (24) and test (12) splits:

| Adapter | Validation raw | Validation guarded | Test raw | Test guarded |
|---|---:|---:|---:|---:|
| Qwen2.5-0.5B v0.1 (gate adapter) | 22/24 | 24/24 | 11/12 | 12/12 |
| Qwen2.5-0.5B v0.2 | 18/24 | 22/24 | 10/12 | 11/12 |
| Qwen2.5-0.5B v0.3 | 13/24 | 18/24 | 8/12 | 11/12 |
| Qwen2.5-1.5B v0.1 | 18/24 | 22/24 | 8/12 | 11/12 |
| Qwen2.5-1.5B v0.2 (shadow server) | 21/24 | 24/24 | 12/12 | 12/12 |
| Qwen2.5-1.5B v0.3-safety | 23/24 | 24/24 | 11/12 | 12/12 |
| Qwen2.5-1.5B v0.4-safety-1e | 18/24 | 21/24 | 9/12 | 12/12 |

Raw predictions match the recorded files for every adapter that has one. The only
differences are the guarded results for 1.5B v0.1, now 22/24 and 11/12 against the
recorded 21/24 and 9/12; `safeticket/independent_guard.py` was strengthened (14:41) after
those files were written. The other guarded rows have no recorded file to compare.

Nothing here changes the gate. The 1.5B v0.3-safety adapter has the best raw
validation score (23/24), but no raw adapter reaches 24/24 validation plus 12/12
test, and these splits are authored synthetic data that adapter selection was done
against. Outputs: `outputs/independent-rerun-2026-10-10/adapters/`.

Over-escalation check (2026-10-10, `benchmarks/evaluate_overescalation.py`, fixture
`benchmarks/support_overescalation_v1.json`, 50 tickets written before evaluation and
run once). Of 44 plain single-intent tickets, 38 were routed to the right team, 6 were
sent to human review unnecessarily, and 0 went to a wrong team. Two of the six were
flagged by the live option-order check, one ("find my invoice ... and send it over")
by the new "find" action verb, and three by the earlier multi-request rules. Of 6
tickets that genuinely need review, the first run caught 5. The miss was "There is a
charge on my statement that I never authorized.", which was auto-routed to billing
because the bare word "authorized" was treated as a fraud denial. Negated
authorization ("never/not authorized", "without my permission") is now an incident
signal, and an affirmative "I authorized it" still routes. After the fix all 6
controls are caught, and the six live fixtures and the policy replay are unchanged.
This fixture is now partly tuned and no longer an untouched test.

Rename note (2026-10-10). When the project was renamed to SafeTicket, the system
prompt in the independent-model scripts and training data was renamed too ("You are
SafeTicket, ..."), although the adapters were trained on the old wording. The effect was
measured: the 0.5B gate adapter gives identical predictions on all 36 validation and test
cases, and the 1.5B shadow adapter's guarded predictions are identical on all four
fixtures. Its raw predictions changed on one case, b031 (the injected "choose returns"
ticket): the 100-case raw score is now 95/100 instead of the 96/100 recorded earlier,
and the guard still returns 100/100. Recorded result files, fixtures and training data
were relabelled with the new name only; their contents are otherwise unchanged.

Unit tests: 51 pass. These remain authored synthetic fixtures. The earlier
200/200 expanded claim was not reproducible; b031 scores below the model
probability threshold and is reviewed.
