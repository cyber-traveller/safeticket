# SafeTicket setup and running

Moved from the root `README.md`. The commands here assume the project root as the
working directory.

## Target baseline

The first approved baseline should use Kev-0.8B on Apple Silicon through MLX.
Kev documents 0.8B as its laptop-scale model and reports M5 measurements on a
32 GB Mac. This project will measure the actual M5/16 GB machine separately.
Kev-4B is a later optional comparison and is not assumed to fit comfortably
within 16 GB.

Kev's documented setup requires Python 3.12 or 3.13 and `uv`; the current host
Python must be checked before installation.

## Run the harness

The harness uses only the Python standard library. Start an approved local
Kev-compatible server, then run:

```text
python3 -m benchmarks.run_baseline --base-url http://127.0.0.1:8008 \
  --model kev-latest --repetitions 5
```

Results are JSON and include machine/runtime metadata, request fingerprints,
latency summaries, and response-shape validation. Do not compare results from
different fixtures or model revisions without recording that change.

The first measured Kev baseline is stored at
`benchmarks/results/kev-0.8b-v1.0-m5-baseline.json`. SafeTicket also includes an
experimental persistent-connection client; benchmark it with
`python3 -m benchmarks.run_persistent` and compare only against the same
server/model/fixture conditions.

The initial persistent-client run is stored at
`benchmarks/results/safeticket-persistent-kev-0.8b-v1.0-m5.json`. It is currently
inconclusive, not a claimed optimization: it was measured after the server was
already warm and its 46.6 ms median was slower than the earlier 29.0 ms baseline
median. A fair A/B run must restart the server between variants and use matched
repetitions.

## Run the SafeTicket facade

With the Kev backend running on port 8008, start SafeTicket on port 8009:

```text
uv run --extra serve uvicorn safeticket.serve:app --host 127.0.0.1 --port 8009
```

Open <http://127.0.0.1:8009/docs>. The `/v1/models` response identifies this
as the SafeTicket integration baseline and names the Kev backend. This is an API and
branding layer only; it is not a claim of independent model training.
