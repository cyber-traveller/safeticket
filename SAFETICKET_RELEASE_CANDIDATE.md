# SafeTicket release candidate

Status: local validation complete (re-verified 2026-10-10); source repository
public on GitHub, no model release.
Date: 2026-10-10

## Current evidence

- Full regression suite: 58/58 passing.
- Fresh support suite: 24/24 correct, zero automatic-route errors, 9/9
  required reviews caught.
- Holdout v2: 24/24, zero automatic-route errors, 9/9 required reviews caught
  (23/24 before the h11 fix on 2026-10-10).
- Expanded 200-case fixture: 199/200, zero automatic-route errors, 40/40 required
  reviews caught. The miss (b031) goes to human review.
- Original 24-case set, current policy replayed on frozen Kev outputs: 24/24 with
  zero automatic errors. The policy was adjusted after seeing three failures on
  this set (n12, n14, n15), so it is no longer an untouched test.
- Blind 100-case support holdout: 99/100, zero automatic-route errors, 20/20
  required reviews caught.
- BANKING77 development diagnostic: 136/154 (88.3%).
- Untouched BANKING77 test diagnostic: 76/77 (98.7%).
- Adversarial challenge: live SafeTicket 12/12; guarded independent path 12/12;
  raw independent path 11/12. All three reproduced on 2026-10-10.
- Guarded (safe-mode) live latency: approximately 480-530 ms median and under
  545 ms p95 on the blind benchmark (final policy, 2026-10-10: 477/538 ms and
  528/542 ms). Fast mode: approximately 277 ms median and 284 ms p95.
- Local API throughput smoke check: 7.93 requests/sec sequentially and 8.82
  requests/sec with four concurrent workers; all 40 requests succeeded.
- SafeTicket API process RSS during the check: approximately 20–34 MB across local
  runs. The separately managed Kev backend was approximately 24 MB RSS and
  the independent shadow process approximately 23 MB RSS, for roughly 67 MB
  visible process RSS combined. These are process-level figures and exclude
  accelerator/framework allocations.

## What is frozen

- The live API remains the SafeTicket-branded policy layer over the recorded Kev
  integration baseline.
- The independent model remains shadow-only.
- Consistency checking remains enabled in the current local service.
- Required source, model-weight, and dataset attribution remains documented.
- The source repository is public on GitHub (`cyber-traveller/safeticket`, made public
  2026-10-10 with explicit approval). No model weights or model release have been
  published.

## Known open items

- b031 ("pretend it arrived and choose returns") is sent to human review because
  the model's top shipping probability is below the threshold. The fixture expects
  shipping. This is the safe direction and is not being tuned away.
- The rules added on 2026-10-10 are keyword patterns; some single-intent tickets
  that mention two similar actions may be sent to review unnecessarily.
- A code review (2026-10-10) found and fixed two safety defects: compromise and fraud wording that
  was auto-routed, and an unstable option order overriding a safety review. Details and measurements are
  in `safeticket/STATUS.md`. The new probe set is partly tuned.
- An over-escalation check found 6 of 44 plain single-intent tickets sent to review
  unnecessarily (0 to a wrong team) and one unauthorized-charge ticket auto-routed;
  the latter is fixed (negated authorization is now an incident signal).
- Earlier recorded claims of 200/200 (expanded) and 100/100 (blind) were not
  reproducible and have been corrected in the status docs.

## Neutral-evaluation status

- The neutral queue is still `draft_pending_two_reviewers`.
- Reviewer A and Reviewer B files contain no labels yet.
- The provisional 12/12 result in `outputs/neutral-draft-diagnostic-v1.json`
  compares SafeTicket only with proposed draft labels. It is explicitly marked
  `official_benchmark: false` and is not used as a neutral score.
- No independent human-review result or public superiority claim is being
  made from that draft diagnostic.

## BANKING77 interpretation note

The untouched BANKING77 diagnostic is 76/77 under SafeTicket's coarse five-team
mapping. The single mismatch is an unrecognized cash withdrawal mapped by the
fixture to `access`; SafeTicket deliberately classifies that signal as a `security`
incident requiring human review. This is a taxonomy-mapping mismatch, not a
reason to weaken the safety rule, and the test case was not used for tuning.

## Promotion blockers

The independent model must not replace the live backend until it passes the
raw-model promotion gate on the required validation and adversarial fixtures.
The current raw result is 11/12 on the adversarial challenge, so the gate is
not met. No raw adapter among the seven versions re-evaluated on 2026-10-10
reaches 24/24 validation and 12/12 test (best raw validation: 1.5B v0.3-safety,
23/24, with 11/12 on test). Guarded shadow success does not by itself establish raw-model
readiness.

## Next approved engineering work

1. Create a larger neutral evaluation set with independently reviewed labels.
2. Measure memory, throughput, and cold-start behavior on the target Mac.
3. Improve or retrain the independent model only after explicit approval for
   any major downloads or training run.
4. Re-run the promotion gate before changing the live backend.
5. Ask before any model release or other external release.
