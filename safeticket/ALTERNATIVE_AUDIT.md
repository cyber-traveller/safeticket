# Open-source decision-engine audit

Updated 2026-10-10. The repositories below are kept under `work/alternatives/`
for inspection only. No source code from them has been copied into SafeTicket.

| Project | License observed | What it contributes | SafeTicket decision |
|---|---|---|---|
| Kev | Apache-2.0 source; model terms kept in provenance | Small Apple-Silicon baseline and System One server | Current backend baseline |
| Laya | License and checkpoint terms must remain attached to its files | Local typed decisions, multilingual and typed-decisions checkpoints | Existing comparison baseline |
| Open Alternative to Jev | Apache-2.0 repository | Option-order permutations, packed/separate isolation, calibration metrics | Adopt the evaluation ideas, not copied implementation |
| jevos | MIT source; model artifact terms still require review | Very small CPU-local Jev-compatible engine | Evaluate as a yes/no and latency specialist |
| Decis | Apache-2.0 server | Self-hosting and engine-selection patterns | Treat as infrastructure, not a new model |

## Techniques worth adding to SafeTicket

1. Measure option-order stability. A choice that changes when labels are
   reordered should be reviewed or averaged across permutations.
2. Report calibration, not just accuracy: Brier score, expected calibration
   error, and confidence/error curves.
3. Separate questions when small-model interference is detected; packed
   questions are faster but can change answers.
4. Keep SafeTicket's fail-closed review band and add a small-model cascade: cheap
   first pass, stronger second pass only for low confidence or instability.
5. Keep all model and source licenses separate from SafeTicket's original policy code.

The downloaded Open Alternative repository's headline 27B results require a
large GPU and are not a suitable target for this 16GB Mac. The local artifact
plan therefore uses a laptop-sized checkpoint for smoke testing and preserves
the larger benchmark claims as unverified external reports.

## SafeTicket adoption result

SafeTicket now exposes an option-order stability gate. With two permutations over the
24-ticket support fixture, the pinned Kev backend produced zero argmax changes;
the largest probability spread was 0.123. The gate remains important for other
backends and future SafeTicket weights even though this particular run was stable.

## jevos smoke and paired fixture result

The local jevos source was built from its MIT repository and its `jevOS-v4`
model artifact was downloaded separately. The default all-CPU-thread launch
failed on this Apple Silicon machine with `Xbyak::Error`; using one inference
thread, a 4096-token context, and no dynamic quantization started successfully.
That configuration is the reproducible compatibility setting for this audit.

On the same 24 support cases and 18 review cases, jevos scored 20/24 support
actions, with 3 automatic errors and 7/9 required reviews caught. Review
comprehension was 14/18 cases fully correct and 50/54 individual judgments.
This is below the current SafeTicket/Kev run, but it is not a general model ranking:
the fixture is synthetic and the implementations use different artifacts.

The downloaded 0.5B Open Alternative checkpoint also passed a local CPU smoke
test using two typed questions in one forward pass. It returned probabilities
and choices as designed. A full apples-to-apples benchmark was not claimed:
the repository's headline results use much larger checkpoints and hardware
that do not fit the 16GB target.
