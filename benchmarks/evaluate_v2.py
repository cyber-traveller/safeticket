"""Paired fixed-policy evaluation. Labels never enter model requests."""
import argparse
import hashlib
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from safeticket.client import SystemOneClient
from safeticket import support, support_v2


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--fixture', default='benchmarks/support_fresh.json')
    parser.add_argument('--output', default='outputs/support-v2-development.json')
    args = parser.parse_args()
    data = Path(args.fixture).read_bytes()
    rows = []
    with SystemOneClient('http://127.0.0.1:8008') as client:
        for i, case in enumerate(json.loads(data)):
            row = dict(case)
            for name, policy in ([('v1', support), ('v2', support_v2)] if i % 2 == 0 else [('v2', support_v2), ('v1', support)]):
                start = time.perf_counter()
                response = client.system_one({'model': 'kev-latest', 'state': case['ticket'], 'questions': policy.QUESTIONS})
                decision = policy.decide(response['answers'], case['ticket']) if name == 'v2' else policy.decide(response['answers'])
                row[name] = {'decision': decision, 'response': response, 'elapsed_ms': (time.perf_counter()-start)*1000}
                predicted = decision['team'] if decision['action'] == 'route' else 'review'
                row[name]['correct'] = predicted == case['team']
            rows.append(row)
    summary = {}
    for name in ('v1', 'v2'):
        routed = [r for r in rows if r[name]['decision']['action'] == 'route']
        summary[name] = {'correct': sum(r[name]['correct'] for r in rows), 'total': len(rows),
                         'automatic_routes': len(routed), 'automatic_errors': sum(not r[name]['correct'] for r in routed),
                         'required_reviews': sum(r['team'] == 'review' for r in rows),
                         'required_reviews_caught': sum(r['team'] == 'review' and r[name]['correct'] for r in rows),
                         'unnecessary_reviews': sum(r['team'] != 'review' and r[name]['decision']['action'] == 'human_review' for r in rows)}
    result = {'measured_at': datetime.now(timezone.utc).isoformat(), 'fixture_sha256': hashlib.sha256(data).hexdigest(),
              'policy_sha256': {n: hashlib.sha256(Path(p.__file__).read_bytes()).hexdigest() for n,p in [('v1', support), ('v2', support_v2)]},
              'method': 'Same tickets and Kev-0.8B backend, alternating order. V2 uses revised questions and policy. Timings are diagnostic only: state cache can benefit the second request. Authored synthetic data; no production claim.',
              'summary': summary, 'rows': rows}
    Path(args.output).write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(summary, indent=2))
    for r in rows:
        if not r['v2']['correct']:
            print(r['id'], r['ticket'], 'expected:', r['team'], 'actual:', r['v2']['decision'])


if __name__ == '__main__':
    main()
