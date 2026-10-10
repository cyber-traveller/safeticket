# SafeTicket provenance

- API and policy code: SafeTicket project source in this directory.
- Current model backend: `jaredpalmer/kev-0.8b@v1.0`.
- Backend status: downloaded locally and served through MLX on Apple Silicon.
- Independent SafeTicket training: not performed.
- Laya evaluation files and environments live outside this package under the
  parent project's `work/` and `outputs/` directories.

The backend identity is returned by `/v1/models` and in `safeticket` response
metadata. This package must not be presented as independently trained until
that status changes with reproducible evidence.
