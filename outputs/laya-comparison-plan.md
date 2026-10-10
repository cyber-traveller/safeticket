# SafeTicket versus Laya: comparison protocol

Status: approved installation and initial fixed-prompt comparison completed.
Both pinned checkpoints were downloaded, SHA-256 verified and evaluated in
isolation using Laya 0.4.1 on MPS. See `laya-comparison-report.md` and the three
`comparison-*.json` files. This initial result supports only a narrow
synthetic support-workflow comparison, not general superiority. The larger
independently labeled, equal-tuning-budget evaluation below remains future work.

## Sources inspected on 2026-10-10

- Repository: https://github.com/NandhaKishorM/laya
- Runtime metadata: https://github.com/NandhaKishorM/laya/blob/main/pyproject.toml
- Router implementation: https://github.com/NandhaKishorM/laya/blob/main/laya/router.py
- Evaluation disclosures: https://github.com/NandhaKishorM/laya/blob/main/BENCHMARKS.md
- Model card: https://huggingface.co/convaiinnovations/laya
- File metadata: https://huggingface.co/api/models/convaiinnovations/laya?blobs=true

The inspected runtime declares version 0.4.1 and Python >=3.10. Its package
metadata and model card declare Apache-2.0. No Laya code or weights have been
copied into SafeTicket. Any future redistribution requires preserving applicable
notices and checking backbone terms separately.

The router normally chooses English or multilingual; its task-specific
checkpoint requires an explicit selection or opt-in task detection. The
comparison will therefore test both English and typed-decisions, rather than
only a default that could disadvantage Laya on support workflows.

## Proposed bounded download

Pin model repository `convaiinnovations/laya` at revision
`7b928d828b7b0e022f929d9bd2e44165aa270148`.

| Selected artifact | Bytes | SHA-256 from Hub metadata |
|---|---:|---|
| English model.safetensors | 842609210 | 891102d372688fc2a094dac56a384bc537b87c63f21f9f3dac0be2b7cbc8d86c |
| typed-decisions/model.safetensors | 842609220 | 4fa56de72383a9d3efa9cfa78955733c81b9fc8067a587ca4beb82c78107a24e |

Together: 1,685,218,430 bytes of weights, plus tokenizer/configuration files
and runtime dependencies. Download only selected subtrees; no multilingual
checkpoint or full bundled snapshot. Use a separate environment to avoid
changing Kev's working dependencies. Pin the runtime source commit/release
before inference and record the resolved dependencies. Verify downloaded
weight hashes. Evaluate one loaded model at a time on the 16 GiB machine.

## Scope and fair comparison

Initial claim scope: English customer-support routing and review decisions
on this Mac. It cannot establish superiority across languages, tasks, hardware,
or every Laya checkpoint. Published T4 timings cannot be compared to local M5
timings. Earlier SafeTicket authored tests are development/regression examples only.

1. Run existing regression fixtures as a compatibility check, never as a fresh
   final benchmark. Verify question rendering, answer semantics, token lengths,
   truncation behavior and selected checkpoint for both Laya variants.
2. Compare raw typed predictions with identical inputs and questions, then
   compare SafeTicket's v2 decision policy applied identically to each backend. Report
   each separately. Do not compare SafeTicket's review-aware output solely against
   Laya's ungated team selection.
3. Provide equal development/tuning opportunity. Because SafeTicket questions were
   developed on Kev, report an additional model-specific tuning comparison
   with equal budgets and untouched test examples. Fit confidence thresholds
   only on development/calibration data, never on final test predictions.
4. Build a larger independently labeled evaluation with clear routing rules,
   ambiguous/multiple requests, incidents, resolved issues, negation and prompt
   injection. Keep related paraphrases in the same split. Synthetic-only
   evidence must be labeled as such; customer-data claims require customer data.
5. Record correct actions, per-category results, automatic routing coverage,
   errors among automatic routes, required reviews caught, and unnecessary
   reviews. Compare risk at matched coverage so deferring everything cannot win.
   Record malformed responses and timeouts as failures, not discarded rows.
6. Measure uncached and cached latency separately using the same client
   transport, document lengths, question counts, warmup counts and machine.
   Pin token/context budgets and verify no truncation. Record memory footprint,
   dtype/backend, model hashes and run order. Repeated latency samples do not
   increase the accuracy sample size.
7. Freeze candidate and protocol before final evaluation. Use paired 95%
   bootstrap intervals over independent tickets (clusters for related cases).
   A quality win requires an interval supporting higher accuracy or lower
   automatic error at matched coverage, without hiding incident regressions.
   Report speed/memory tradeoffs separately; if results are inconclusive, say so.

After the baseline, use observed development failures to improve SafeTicket, then
evaluate the frozen candidate once on the untouched final test set. No promise
to beat Laya is made in advance of measurement.
