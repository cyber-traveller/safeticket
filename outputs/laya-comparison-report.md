# SafeTicket versus Laya: initial local comparison

All three backends received the same 24 newly authored synthetic tickets and the same questions. The SafeTicket support-v2 policy was also applied identically to all three. No tuning was performed on this test set.

| Measure | SafeTicket / Kev-0.8B | Laya English | Laya typed-decisions |
|---|---:|---:|---:|
| Raw team answers correct | 17 | 14 | 14 |
| Correct actions with identical policy | 24 | 17 | 15 |
| Automatic routes | 15 | 10 | 6 |
| Incorrect automatic routes | 0 | 2 | 0 |
| Required reviews caught (of 9) | 9 | 9 | 9 |
| Unnecessary reviews | 0 | 5 | 9 |

## Limits

This is a small synthetic, English support-only comparison. The prompts and policy were developed on Kev, so this fixed-prompt experiment favors SafeTicket. It is not an equal-budget tuning comparison or proof of general superiority. A paired bootstrap interval is provided in the JSON; it describes uncertainty on these authored cases, not real-world representativeness.

Both Laya checkpoints use the pinned Hub revision 7b928d828b7b0e022f929d9bd2e44165aa270148 and verified SHA-256 weights. Runtime: Laya 0.4.1. Full configurations, input-truncation checks, responses and hashes are in the per-backend JSON files.

Laya runs through its local SDK and Kev through HTTP, with different dtypes and caching. Diagnostic times must not be used as a latency ranking. No model weights were trained or changed. SafeTicket still uses Kev weights.

The JSON summary also reports raw routing errors at matched 25% and 50% coverage, without selecting thresholds using the test labels. Human review is not counted as an automatic correct route.
