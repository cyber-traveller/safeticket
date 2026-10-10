#!/bin/sh
set -eu
exec .venv/bin/python -m uvicorn safeticket.serve:app --host "${SAFETICKET_HOST:-127.0.0.1}" --port "${SAFETICKET_PORT:-8009}"
