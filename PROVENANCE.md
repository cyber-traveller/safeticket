# Provenance and licensing

This file is deliberately explicit so the project does not obscure its
starting point.

## Upstream software

Kev repository: <https://github.com/jaredpalmer/kev>

- Inspected repository license: Apache License 2.0.
- Copyright notice observed in upstream license: Copyright 2026 Jared Palmer.
- No upstream source files are copied into the current SafeTicket scaffold.
- If upstream code is copied or modified later, preserve `LICENSE`, applicable
  copyright/attribution notices, and add a prominent notice to each modified
  file as required by Apache-2.0 section 4.

## Model artifacts

Model weights are separate artifacts and are not included here.

| Artifact | Upstream revision | Declared license | Base model | Local status |
|---|---:|---|---|---|
| `jaredpalmer/kev-0.8b` | `9a45d25e` (`v1.0`) | Apache-2.0 for adapter/head | `Qwen/Qwen3.5-0.8B-Base` (Apache-2.0) | Downloaded locally; served via MLX |
| `jaredpalmer/kev-4b` | `139fdd94` (`v1.0`) | Apache-2.0 for adapter/head | `Qwen/Qwen3.5-4B-Base` (Apache-2.0) | Not downloaded |
| `jaredpalmer/kev-9b` | `b5d8c18e` (`v2`) | Apache-2.0 for adapter/head | `Qwen/Qwen3.5-9B-Base` (Apache-2.0) | Not downloaded |
| `jaredpalmer/kev-27b` | `28be62e9` (`v2`) | Apache-2.0 for full weights | `Qwen/Qwen3.8-27B` (Apache-2.0) | Not downloaded |

Before any redistribution, re-check the exact model-card and base-model
licenses at the pinned revision, preserve their notices, and record checksums.

## Local baseline evidence

- Target: arm64 macOS 27.0.1 with 16 GiB installed memory.
- Kev source checkout: commit `fc4a17e194bca35a48c57211392ec49ea54a94ac`.
- Model server: `jaredpalmer/kev-0.8b@v1.0`, MLX/bfloat16 on MPS.
- Hugging Face snapshot observed by the server: `bf75a6a8848ea6960ff2ed108d9ed44c2941174f`.
- Raw baseline: `benchmarks/results/kev-0.8b-v1.0-m5-baseline.json`.
- The baseline fixture's SHA-256 is stored in the raw result; no benchmark
  result is being presented as a SafeTicket model-quality or training claim.

## Evidence policy

SafeTicket will not claim original training, independent weights, benchmark wins, or
optimization gains until the relevant experiment, inputs, revision, hardware,
software versions, and raw results are recorded.
