# SafeTicket

[![tests](https://github.com/cyber-traveller/safeticket/actions/workflows/tests.yml/badge.svg)](https://github.com/cyber-traveller/safeticket/actions/workflows/tests.yml)

SafeTicket is the decision API and support policy owned by this project.

The package exposes:

- `safeticket.serve:app` — SafeTicket HTTP API and Swagger documentation.
- `safeticket.support_v2` — active support-routing policy.
- `safeticket.client.SystemOneClient` — dependency-free client for typed decisions.

The current model backend is recorded explicitly in every API response:
`jaredpalmer/kev-0.8b@v1.0`. SafeTicket has not yet trained independent weights.

## Start locally

Run the Kev backend on port 8008, then from the project root:

```text
.venv/bin/python -m uvicorn safeticket.serve:app --host 127.0.0.1 --port 8009
```

Open <http://127.0.0.1:8009/docs>.

## Support endpoint

`POST /v1/support/decide`

```json
{"ticket":"I was charged twice for my order."}
```

The response includes a route or `human_review`, the model evidence, and the
active policy version. The policy requests review for uncertainty, multiple
unresolved requests, and possible unauthorized access or payments.
It also recognizes an explicit receipt, invoice, or billing-statement request
as billing when the model has not detected an incident or multiple unresolved
requests.

The live service supports two explicit profiles through `SAFETICKET_MODE`:

- `safe` (default): runs the option-order robustness check; unstable choices
  fail closed to `human_review`.
- `fast`: skips that extra check for lower latency and should be used only when
  the caller accepts the weaker robustness guarantee.

The older `SAFETICKET_CONSISTENCY_CHECK=1|0` setting remains supported when
`SAFETICKET_MODE` is unset. If both are supplied, `SAFETICKET_MODE` takes precedence.

The guarded configuration was measured at 99/100 on the blind support fixture
with approximately 480-530 ms median and under 545 ms p95 latency (two safe-mode
runs, 2026-10-10: 477 ms / 538 ms and 528 ms / 542 ms). A fast-mode run measured
approximately 277 ms median and 284 ms p95 with the same fixture result.
Safe mode remains the recommended live configuration.
Independent shadow calls are bounded by `SAFETICKET_SHADOW_TIMEOUT_SECONDS` (default
30 seconds), and backend calls by `SAFETICKET_BACKEND_TIMEOUT_SECONDS` (default 120
seconds).

## Latest results (2026-10-10)

Live API, safe mode, Kev backend. Every fixture below is authored synthetic data,
not production evidence.

| Fixture | Result | Wrong automatic routes | Required reviews caught |
|---|---:|---:|---:|
| Blind (100) | 99/100 | 0 | 20/20 |
| Expanded (200) | 199/200 | 0 | 40/40 |
| Holdout v2 (24) | 24/24 | 0 | 9/9 |
| Fresh (24) | 24/24 | 0 | 9/9 |
| Adversarial v1 (12) | 12/12 | 0 | 4/4 |
| Challenge v1 (12) | 12/12 | 0 | 4/4 |

- The one miss on the blind and expanded fixtures is the same ticket (b031, an
  injected "pretend it arrived" instruction). It goes to human review, the safe
  direction.
- The policy was adjusted after seeing failures on the holdout (h11) and on the
  original 24-case set (n12, n14, n15), so those sets are no longer untouched
  tests. The original set replays at 24/24 on the frozen Kev outputs.
- The independent adapter is shadow-only. Its raw model scores 22/24 validation
  and 11/12 test (guarded: 24/24 and 12/12) and is not ready to replace the live
  backend. See `STATUS.md` for all adapter versions.
- Fast mode is about 277 ms median; safe mode is about 480-530 ms.
- 51 unit tests pass.

Earlier claims of 200/200 (expanded) and 100/100 (blind) could not be reproduced.
Details and the full evidence log are in `STATUS.md`.

See the parent project’s `NOTICE` and `PROVENANCE.md` for attribution.
