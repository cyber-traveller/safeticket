# Combined SafeTicket benchmark

| Backend | Support action accuracy | Support automatic errors | Support reviews caught | Review cases fully correct | Review individual judgments |
|---|---:|---:|---:|---:|---:|
| SafeTicket / Kev backend | 24/24 | 0/15 | 9/9 | 17/18 | 53/54 |
| Laya English | 17/24 | 2/10 | 9/9 | 14/18 | 49/54 |
| Laya typed-decisions | 15/24 | 0/6 | 9/9 | 16/18 | 51/54 |

## Current-policy replay (2026-10-10)

Support columns above are the recorded results. The replay table applies the current support-v2 policy (2026-10-10) to the same frozen model outputs with no new inference; policy rules were adjusted after seeing the n12, n14 and n15 failures, so replay results are no longer an untouched test.

| Backend | Support action accuracy | Support automatic errors | Support reviews caught | Unnecessary reviews |
|---|---:|---:|---:|---:|
| SafeTicket / Kev backend | 24/24 | 0/15 | 9/9 | 0 |
| Laya English | 19/24 | 1/11 | 9/9 | 4 |
| Laya typed-decisions | 19/24 | 0/10 | 9/9 | 5 |

SafeTicket / Kev backend scores highest on both frozen synthetic tasks, but this is not a neutral ranking: the prompts and support policy were developed on Kev, and the other backends run under that same policy. The support score includes the same SafeTicket review policy applied to every backend; support automatic-route errors and review coverage are reported separately. The review score counts a case correct only when all three judgments are correct.

## Limits

42 authored English synthetic cases total. Prompts and the support policy were developed on Kev, so this is not a neutral model leaderboard. Cases are not customer data, not independent samples for each question, and not sufficient to establish general superiority. SafeTicket still uses Kev weights. Latencies are excluded because backends use different transports and runtimes.

The complete per-case predictions remain in the JSON artifacts listed above.
