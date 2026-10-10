"""Evaluate the frozen support holdout through the running SafeTicket endpoint.

Labels are used only after inference for scoring. They never enter requests.
"""
import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from safeticket.client import SystemOneClient


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--base-url', default='http://127.0.0.1:8009')
    parser.add_argument('--fixture', default='benchmarks/support_holdout_v2.json')
    parser.add_argument('--output', default='outputs/safeticket-holdout-v2.json')
    args = parser.parse_args()

    fixture = Path(args.fixture).read_bytes()
    cases = json.loads(fixture)
    rows = []
    with SystemOneClient(args.base_url) as client:
        for case in cases:
            response = client.support_decide(case['ticket'])
            prediction = response.get('decision', {})
            predicted = prediction.get('team') if prediction.get('action') == 'route' else 'review'
            rows.append({
                'id': case['id'],
                'expected': case['team'],
                'predicted': predicted,
                'correct': predicted == case['team'],
                'response': response,
            })

    automatic = [r for r in rows if r['predicted'] != 'review']
    required_reviews = [r for r in rows if r['expected'] == 'review']
    report = {
        'measured_at': datetime.now(timezone.utc).isoformat(),
        'fixture_sha256': hashlib.sha256(fixture).hexdigest(),
        'method': 'Frozen synthetic holdout through SafeTicket support endpoint; labels scored after inference.',
        'summary': {
            'correct': sum(r['correct'] for r in rows),
            'total': len(rows),
            'automatic_routes': len(automatic),
            'automatic_errors': sum(not r['correct'] for r in automatic),
            'required_reviews': len(required_reviews),
            'required_reviews_caught': sum(r['correct'] for r in required_reviews),
            'unnecessary_reviews': sum(r['expected'] != 'review' and r['predicted'] == 'review' for r in rows),
        },
        'rows': rows,
        'limitations': 'Synthetic authored holdout; not production data and not evidence of general model superiority.',
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report['summary'], indent=2))


if __name__ == '__main__':
    main()
