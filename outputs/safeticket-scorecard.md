# SafeTicket evidence scorecard

Updated 2026-10-10. These are controlled synthetic support-routing results,
not a general model leaderboard.

The "SafeTicket vs ..." rows below compare systems run under SafeTicket's own policy on
project-authored cases that the policy was tuned on. Differences of a few cases
on 12-24 cases are not evidence that one system is better.

| Comparison | Result |
|---|---:|
| Live SafeTicket, expanded 200-case policy fixture | 199/200 (re-run 2026-10-10) |
| Live SafeTicket, 100-case independent comparison fixture | 99/100 (re-run 2026-10-10; recorded 100/100) |
| Guarded independent v0.2, same 100 cases | 100/100 (re-run 2026-10-10, reproduced) |
| Raw independent v0.2, same 100 cases | 96/100 (re-run 2026-10-10, reproduced); 95/100 after the prompt rename |
| SafeTicket vs Kev, frozen 24-case comparison | 18/24 vs 17/24 |
| SafeTicket vs Jev, 24-case support comparison | 24/24 vs 20/24 |
| SafeTicket vs Laya English, 24-case comparison | 21/24 vs 17/24 |
| SafeTicket vs Laya typed decisions, 24-case comparison | 21/24 vs 15/24 |
| SafeTicket vs Open Alternative support challenge | 12/12 vs 3/12 |
| BANKING77 coarse-mapping diagnostic | SafeTicket 76/77 test (98.7%); 136/154 dev (88.3%) |

## Live re-run, 2026-10-10 (final policy, safe mode)

| Fixture | Result | Automatic-route errors | Required reviews caught |
|---|---:|---:|---:|
| Blind (100) | 99/100 | 0 | 20/20 |
| Expanded (200) | 199/200 | 0 | 40/40 |
| Holdout v2 (24) | 24/24 | 0 | 9/9 |
| Fresh (24) | 24/24 | 0 | 9/9 |
| Adversarial v1 (12) | 12/12 | 0 | 4/4 |
| Challenge v1 (12) | 12/12 | 0 | 4/4 |
| Original 24-case set, policy replay on frozen Kev outputs | 24/24 | 0 | 9/9 |

Blind-fixture latency: fast 277 ms median / 284 ms p95; safe 477-528 ms median /
538-542 ms p95. Both modes score 99/100. The two remaining misses (blind and
expanded) are the same case, b031, which goes to human review.

## Independent adapter versions, re-run 2026-10-10

Validation (24) and test (12) splits, raw model and with the safety guard. Raw
predictions reproduce the recorded files; 1.5B v0.1 guarded improved over its
recorded 21/24 and 9/12 because the guard was strengthened afterwards.

| Adapter | Validation raw | Validation guarded | Test raw | Test guarded |
|---|---:|---:|---:|---:|
| Qwen2.5-0.5B v0.1 (gate adapter) | 22/24 | 24/24 | 11/12 | 12/12 |
| Qwen2.5-0.5B v0.2 | 18/24 | 22/24 | 10/12 | 11/12 |
| Qwen2.5-0.5B v0.3 | 13/24 | 18/24 | 8/12 | 11/12 |
| Qwen2.5-1.5B v0.1 | 18/24 | 22/24 | 8/12 | 11/12 |
| Qwen2.5-1.5B v0.2 (shadow server) | 21/24 | 24/24 | 12/12 | 12/12 |
| Qwen2.5-1.5B v0.3-safety | 23/24 | 24/24 | 11/12 | 12/12 |
| Qwen2.5-1.5B v0.4-safety-1e | 18/24 | 21/24 | 9/12 | 12/12 |

No raw adapter reaches 24/24 validation plus 12/12 test, so none is ready to
replace the live path. The adapters were selected against these same splits, so
the scores are optimistic. Outputs: `outputs/independent-rerun-2026-10-10/`.

## What this supports

On SafeTicket's own synthetic support-routing fixtures, the policy layer sends risky
tickets to human review reliably (zero wrong automatic routes). It matches or
exceeds the other systems' scores on those fixtures, but this is not a fair
comparison: every system ran under SafeTicket's policy, the prompts and policy were
developed on Kev and tuned on these cases, and the sets are small. The guarded
independent shadow path matches live SafeTicket on the bounded 100-case comparison.

## What this does not support

It does not prove universal superiority, production accuracy, or that the raw
independent model is ready to replace Kev. The live API still uses the Kev
backend, and all fixtures are authored synthetic cases. A neutral external
benchmark and independently labeled data are still required before publishing
or making broad performance claims.

BANKING77 is not a direct leaderboard result: its 77 banking intents were
mapped into SafeTicket's five coarse teams by a local script. See
`benchmarks/BANKING77_PROVENANCE.md` for source and license details.

Note (2026-10-10): these are recorded results from earlier policy versions. Replaying the current policy on the frozen outputs gives SafeTicket/Kev 24/24, Laya English 19/24 and Laya typed-decisions 19/24; see `outputs/support-policy-replay.md` and `safeticket/STATUS.md`. The policy rules were adjusted after seeing the n12, n14 and n15 failures.
