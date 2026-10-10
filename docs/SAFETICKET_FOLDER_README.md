# SafeTicket project folder

[![tests](https://github.com/cyber-traveller/safeticket/actions/workflows/tests.yml/badge.svg)](https://github.com/cyber-traveller/safeticket/actions/workflows/tests.yml)

This is the dedicated SafeTicket entry point:

`/Users/joel/Documents/Codex/SafeTicket`

Apart from this README, everything in this folder is a symlink to the canonical project directory below,
where the real files live: `safeticket/` (API, policy, guard, client, and its docs),
`benchmarks`, `tests`, `work` (experiments), `outputs`, `.venv`,
`SAFETICKET_PROGRESS.md`, `SAFETICKET_RELEASE_CANDIDATE.md`, `LICENSE` and `NOTICE`. Edits through either path change
the same files. The project directory is a git repository (public on GitHub as
`cyber-traveller/safeticket`); model weights,
environments and upstream checkouts under `work/` are not tracked.

Start from the canonical project directory when running commands:

`/Users/joel/Documents/Codex/2026-10-10/referenced-chatgpt-conversation-this-is-an`

## Latest results (2026-10-10)

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
  injected instruction). It goes to human review.
- The policy was adjusted after failures on the holdout and the original 24-case
  set, so those sets are now regression tests.
- The independent Qwen adapter is shadow-only; its raw model is not ready to
  replace the live backend.
- Latency on the blind set: about 277 ms median in fast mode, 480-530 ms in safe
  mode. 58 unit tests pass.
- Earlier claims of 200/200 (expanded) and 100/100 (blind) were not reproducible.

Details: `safeticket/README.md`, `safeticket/STATUS.md`, `SAFETICKET_PROGRESS.md`, and
`SAFETICKET_RELEASE_CANDIDATE.md` in this folder. The result files, including the gate
(`outputs/safeticket-benchmark-gate.md`) and scorecard (`outputs/safeticket-scorecard.md`), are
in `outputs/` here.


## License

SafeTicket's own code, benchmarks, and documentation are licensed under Apache-2.0
(`LICENSE` in this folder; the copyright line is in `NOTICE`, also here).
Third-party material keeps its own terms: the Kev backend and weights, the Qwen2.5
base models, and the BANKING77 dataset (CC BY 4.0). See the project `README.md`
License section and the `PROVENANCE.md` files.
