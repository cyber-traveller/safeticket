"""Evaluate live, raw-independent, and guarded-independent SafeTicket paths."""
import json
import os
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = Path(os.environ.get('SAFETICKET_CHALLENGE_FIXTURE', str(ROOT / 'benchmarks' / 'support_challenge_v1.json'))).expanduser().resolve()


def post(url, ticket):
    req = urllib.request.Request(url, data=json.dumps({'ticket': ticket}).encode(), headers={'content-type': 'application/json'})
    start = time.perf_counter()
    with urllib.request.urlopen(req, timeout=90) as response:
        return json.load(response), (time.perf_counter() - start) * 1000


def main():
    cases = json.loads(FIXTURE.read_text())
    def evaluate(case):
        live, live_ms = post(os.environ.get('SAFETICKET_LIVE_URL', 'http://127.0.0.1:8009') + '/v1/support/decide', case['ticket'])
        shadow, shadow_ms = post(os.environ.get('SAFETICKET_SHADOW_URL', 'http://127.0.0.1:8019') + '/decide', case['ticket'])
        live_team = live.get('decision', {}).get('team') if live.get('decision', {}).get('action') == 'route' else 'review'
        return {
            **case,
            'live_team': live_team,
            'raw_independent_team': shadow.get('raw_team', shadow.get('team')),
            'guarded_independent_team': shadow.get('team'),
            'live_correct': live_team == case['team'],
            'raw_independent_correct': shadow.get('raw_team', shadow.get('team')) == case['team'],
            'guarded_independent_correct': shadow.get('team') == case['team'],
            'live_latency_ms': live_ms,
            'shadow_latency_ms': shadow_ms,
            'guard_reason': shadow.get('reason'),
        }
    workers = max(1, min(4, int(os.environ.get('SAFETICKET_BENCHMARK_WORKERS', '4'))))
    with ThreadPoolExecutor(max_workers=workers) as pool:
        rows = list(pool.map(evaluate, cases))
    summary = {
        name: sum(row[f'{name}_correct'] for row in rows)
        for name in ('live', 'raw_independent', 'guarded_independent')
    }
    summary['total'] = len(rows)
    report = {
        'measured_at': datetime.now(timezone.utc).isoformat(),
        'fixture': str(FIXTURE.relative_to(ROOT)) if FIXTURE.is_relative_to(ROOT) else str(FIXTURE),
        'limitations': '12 newly authored synthetic challenge cases, evaluated once. Not production data and not evidence of general superiority.',
        'summary': summary,
        'rows': rows,
    }
    out = Path(os.environ.get('SAFETICKET_CHALLENGE_OUT', str(ROOT / 'outputs' / 'shadow-challenge-v1.json')))
    out.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
