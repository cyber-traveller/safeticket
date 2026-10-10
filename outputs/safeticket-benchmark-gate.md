# SafeTicket benchmark gate

| System | Holdout | Adversarial | Replacement status |
|---|---:|---:|---|
| Live SafeTicket policy | 24/24 | 12/12 | Passes current safety gate |
| Independent SafeTicket adapter | 22/24 validation | 11/12 | Raw model not ready |
| Independent SafeTicket + safety guard | 24/24 | 12/12 | Passes current fixtures; shadow only |
| Open Alternative 0.5B | not run | 3/12 challenge | Rejected for support routing |
| jevos | 20/24 support | not run on this adversarial fixture | Comparator only |
| Laya | See combined benchmark | See combined benchmark | Comparator only |

## Independent adapter versions (re-run 2026-10-10)

| Adapter | Validation raw | Validation guarded | Test raw | Test guarded |
|---|---:|---:|---:|---:|
| Qwen2.5-0.5B v0.1 (gate adapter) | 22/24 | 24/24 | 11/12 | 12/12 |
| Qwen2.5-0.5B v0.2 | 18/24 | 22/24 | 10/12 | 11/12 |
| Qwen2.5-0.5B v0.3 | 13/24 | 18/24 | 8/12 | 11/12 |
| Qwen2.5-1.5B v0.1 | 18/24 | 22/24 | 8/12 | 11/12 |
| Qwen2.5-1.5B v0.2 (shadow server) | 21/24 | 24/24 | 12/12 | 12/12 |
| Qwen2.5-1.5B v0.3-safety | 23/24 | 24/24 | 11/12 | 12/12 |
| Qwen2.5-1.5B v0.4-safety-1e | 18/24 | 21/24 | 9/12 | 12/12 |

Authored synthetic fixtures, different model artifacts and runtimes, no production data, and no general superiority claim. The live SafeTicket policy still uses Kev weights.
