# Independent SafeTicket model gate

SafeTicket currently improves decision policy, robustness, and safety around a pinned
Kev backend. It must not be described as an independently trained model yet.

## Required before an independent-model claim

1. Choose and record a base model and its license.
2. Record the model-weight and dataset licenses separately from SafeTicket source.
3. Create train, validation, and test splits before tuning.
4. Keep the test labels hidden from policy and training changes.
5. Compare the candidate against the pinned Kev, jevos, and Laya baselines on
   the same frozen cases.
6. Require no regression on unsafe automatic routes, calibration, or option
   order stability.
7. Store model hashes, prompts, hardware, seed, and evaluation artifacts.

## Target metrics

- Support: zero unsafe automatic routes on the frozen safety suite.
- Review recall: 100% on required human-review cases.
- Review comprehension: at least 53/54 individual judgments on the current
  fixture, then higher performance on an independently labeled test set.
- Calibration: report Brier score and expected calibration error, not accuracy
  alone.
- Robustness: option-order changes must trigger review or remain stable.
- Reproducibility: a second run with the recorded seed must reproduce results.

## Current status

The policy layer passes 24/24 on both current support fixtures and 12/12 on
the authored adversarial fixture. These are development gates, not evidence of
general superiority. No training model, dataset, or new weights have been
downloaded for this gate yet.
