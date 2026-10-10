"""Fresh authored evaluation of the live SafeTicket API; policy remains unchanged."""
import hashlib
import json
import statistics
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


def post(payload):
    req = urllib.request.Request('http://127.0.0.1:8009/v1/support/decide', data=json.dumps(payload).encode(), headers={'Content-Type': 'application/json'})
    start = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.status, json.load(r), (time.perf_counter()-start)*1000
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read()), (time.perf_counter()-start)*1000


def main():
    fixture = Path(__file__).with_name('support_fresh.json')
    rows = []
    for case in json.loads(fixture.read_text()):
        status, response, latency = post({'ticket': case['ticket']})
        decision = response.get('decision', {})
        predicted = decision.get('team') if decision.get('action') == 'route' else 'review'
        rows.append({**case, 'status': status, 'response': response, 'latency_ms': latency,
                     'correct': status == 200 and predicted == case['team']})
    validation = []
    for payload in ({}, {'ticket': ''}, {'ticket': 42}, {'ticket': 'x'*16001}, {'ticket': '   '}):
        status, _, _ = post(payload)
        validation.append({'case': 'whitespace' if payload == {'ticket':'   '} else str(payload)[:70], 'status':status, 'expected':422, 'passed':status == 422})
    routed = [r for r in rows if r['response'].get('decision', {}).get('action') == 'route']
    review = [r for r in rows if r['team'] == 'review']
    summary = {'requests':len(rows), 'successful_http_responses':sum(r['status']==200 for r in rows),
               'correct_final_actions':sum(r['correct'] for r in rows), 'automatic_routes':len(routed),
               'automatic_route_errors':sum(not r['correct'] for r in routed),
               'required_reviews':len(review), 'required_reviews_caught':sum(r['correct'] for r in review),
               'latency_median_ms':statistics.median(r['latency_ms'] for r in rows),
               'validation_checks_passed':sum(v['passed'] for v in validation), 'validation_checks':len(validation)}
    report = {'measured_at':datetime.now(timezone.utc).isoformat(), 'fixture_sha256':hashlib.sha256(fixture.read_bytes()).hexdigest(),
              'policy_sha256':hashlib.sha256(Path('safeticket/support.py').read_bytes()).hexdigest(),
              'limitations':'24 newly authored synthetic examples, evaluated once without tuning. Not customer data or a production accuracy estimate. Labels were written before running inference.',
              'summary':summary, 'rows':rows, 'validation':validation}
    Path('outputs/fresh-support-test.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(summary, indent=2))
    for r in rows:
        if not r['correct']:
            print(r['id'], r['ticket'], 'EXPECTED', r['team'], 'ACTUAL', r['response'].get('decision'))
    print('Validation', validation)


if __name__ == '__main__':
    main()
