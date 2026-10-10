"""Evaluate the live SafeTicket policy on the held-out 100-case fixture."""
import json
import os
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = Path(os.environ.get('SAFETICKET_CHALLENGE_FIXTURE', str(ROOT / 'benchmarks' / 'support_blind_v1.json'))).expanduser().resolve()
URL = os.environ.get('SAFETICKET_LIVE_URL', 'http://127.0.0.1:8009') + '/v1/support/decide'


def run(case):
    request = urllib.request.Request(URL, data=json.dumps({'ticket': case['ticket']}).encode(), headers={'content-type': 'application/json'})
    start = time.perf_counter()
    with urllib.request.urlopen(request, timeout=120) as response:
        payload = json.load(response)
    team = payload.get('decision', {}).get('team') if payload.get('decision', {}).get('action') == 'route' else 'review'
    return {**case, 'predicted': team, 'correct': team == case['team'], 'action': payload.get('decision', {}).get('action'), 'reason': payload.get('decision', {}).get('reason'), 'latency_ms': (time.perf_counter() - start) * 1000}


def main():
    cases = json.loads(FIXTURE.read_text())
    workers = max(1, min(4, int(os.environ.get('SAFETICKET_BENCHMARK_WORKERS', '4'))))
    with ThreadPoolExecutor(max_workers=workers) as pool:
        rows = list(pool.map(run, cases))
    review = [row for row in rows if row['team'] == 'review']
    routed = [row for row in rows if row['action'] == 'route']
    summary = {
        'correct': sum(row['correct'] for row in rows), 'total': len(rows),
        'automatic_routes': len(routed), 'automatic_route_errors': sum(not row['correct'] for row in routed),
        'required_reviews': len(review), 'required_reviews_caught': sum(row['correct'] for row in review),
        'validation_status': 'not part of this fixture',
    }
    out = Path(os.environ.get('SAFETICKET_CHALLENGE_OUT', str(ROOT / 'outputs' / 'live-blind-v1.json')))
    fixture_name = str(FIXTURE.relative_to(ROOT)) if FIXTURE.is_relative_to(ROOT) else str(FIXTURE)
    out.write_text(json.dumps({'fixture': fixture_name, 'limitations': f'{len(cases)} authored synthetic cases, not production evidence.', 'summary': summary, 'rows': rows}, indent=2) + '\n')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
