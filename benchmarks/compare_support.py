"""Matched live comparison: Kev argmax vs SafeTicket's unchanged support policy."""
import hashlib
import json
import statistics
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from safeticket.support import QUESTIONS, THRESHOLD, decide


def call(variant, ticket):
    url = ('http://127.0.0.1:8008/v1/systemone' if variant == 'kev'
           else 'http://127.0.0.1:8009/v1/support/decide')
    payload = ({'state': ticket, 'model': 'kev-latest', 'questions': QUESTIONS}
               if variant == 'kev' else {'ticket': ticket})
    request = urllib.request.Request(url, data=json.dumps(payload).encode(),
                                     headers={'Content-Type': 'application/json'})
    start = time.perf_counter()
    with urllib.request.urlopen(request, timeout=60) as response:
        result = json.load(response)
    return result, (time.perf_counter() - start) * 1000


def metrics(rows, variant):
    routed = [r for r in rows if r[variant] != 'review']
    errors = sum(r[variant] != r['team'] for r in routed)
    return {'correct_actions': sum(r[variant] == r['team'] for r in rows),
            'automatic_routes': len(routed), 'automatic_errors': errors,
            'automatic_error_rate': errors / len(routed) if routed else None,
            'required_reviews_caught': sum(r['team'] == 'review' and r[variant] == 'review' for r in rows),
            'unnecessary_reviews': sum(r['team'] != 'review' and r[variant] == 'review' for r in rows)}


def main():
    fixture = Path(__file__).with_name('support_fresh.json')
    rows, timings = [], {'kev': [], 'safeticket': []}
    for index, case in enumerate(json.loads(fixture.read_text())):
        # Warm both paths for each identical state; exclude these calls from timing.
        baseline, _ = call('kev', case['ticket'])
        facade, _ = call('safeticket', case['ticket'])
        same = baseline['answers'] == facade['evidence']['answers']
        expected_policy = decide(baseline['answers'])
        if not same or expected_policy != facade['decision']:
            raise RuntimeError(f"Unmatched evidence or policy on {case['id']}; comparison aborted")
        prediction = facade['decision']['team'] if facade['decision']['action'] == 'route' else 'review'
        samples = {'kev': [], 'safeticket': []}
        # Counterbalanced ABBA/BAAB order limits drift and first-position bias.
        order = ('kev', 'safeticket', 'safeticket', 'kev') if index % 2 == 0 else ('safeticket', 'kev', 'kev', 'safeticket')
        for variant in order:
            result, elapsed = call(variant, case['ticket'])
            answers = result['answers'] if variant == 'kev' else result['evidence']['answers']
            if answers != baseline['answers']:
                raise RuntimeError('Predictions changed between repeated requests')
            samples[variant].append(elapsed)
            timings[variant].append(elapsed)
        rows.append({**case, 'kev': baseline['answers']['team']['choice'], 'safeticket': prediction,
                     'identical_model_answers': same, 'answers': baseline['answers'],
                     'decision': facade['decision'], 'latency_samples_ms': samples})
    summary = {v: metrics(rows, v) for v in ('kev', 'safeticket')}
    for v in summary:
        summary[v]['warm_median_ms'] = statistics.median(timings[v])
        summary[v]['timed_requests'] = len(timings[v])
    summary['safeticket_fixes'] = [r['id'] for r in rows if r['kev'] != r['team'] and r['safeticket'] == r['team']]
    summary['safeticket_regressions'] = [r['id'] for r in rows if r['kev'] == r['team'] and r['safeticket'] != r['team']]
    report = {'measured_at': datetime.now(timezone.utc).isoformat(),
              'fixture_sha256': hashlib.sha256(fixture.read_bytes()).hexdigest(),
              'policy_sha256': hashlib.sha256(Path('safeticket/support.py').read_bytes()).hexdigest(),
              'questions': QUESTIONS, 'threshold': THRESHOLD,
              'method': 'Same 24 previously evaluated authored cases, same questions and backend. Kev baseline uses team argmax (including review); SafeTicket adds its uncertainty/incident policy. All model answers must match. Warm both paths per ticket; time two requests per path in counterbalanced order. No tuning.',
              'limitations': 'Synthetic development data, previously inspected. Not an independent holdout or a comparison to every possible Kev application policy. Warm cached latency only; no cold-start or throughput claim.',
              'summary': summary, 'rows': rows}
    Path('outputs/safeticket-vs-kev.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
