# Local Laya installation record

- Isolated runtime: `work/laya-env`, Python 3.13.15, Laya 0.4.1,
  PyTorch 2.8.0, Transformers 5.17.0. Further dependency versions are recorded
  in each Laya result's metadata.
- Model directory: `work/laya-models`.
- Hub revision: `7b928d828b7b0e022f929d9bd2e44165aa270148`.
- Both model SHA-256 hashes matched the previously inspected Hub metadata;
  exact hashes are in `comparison-english.json` and
  `comparison-typed-decisions.json`.
- Laya inference used explicit MPS eager execution and offline Hub mode.
  Each Laya checkpoint ran in a separate process which exited after evaluation.
- SafeTicket's existing Kev server was unchanged. Its `/v1/models` response reported
  Kev-0.8B v1.0, Qwen3.5-0.8B-Base, MLX/bfloat16, temperature
  2.3510958125672174, and state truncation disabled.
- All Laya questions retained their complete instruction and option tokens,
  and all tickets fit without truncation. Head budget was 384, context 512.
- Laya issued its built-in calibration clamp warning for the 11-or-more-option
  bucket. This experiment uses five-option choice questions and binary noul
  questions, not that bucket; no calibration values were manually changed.
- Laya code and weights remain in the separate evaluation workspace. They
  were not incorporated into SafeTicket's inference implementation or republished.
