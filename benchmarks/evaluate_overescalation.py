"""Measure unnecessary human-review escalations on plain single-intent tickets.

Runs the live SafeTicket API once on the fixture, then replays the recorded model
evidence through the pre-2026-10-10 policy (passed with --old-policy-dir) to
attribute any escalation to the rules added that day.
"""
import argparse
import importlib.util
import json
import sys
import urllib.request
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from safeticket import support_v2 as new_policy  # noqa: E402


def load_old(path):
    spec = importlib.util.spec_from_file_location('support_v2_old', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def final(decision):
    return decision['team'] if decision['action'] == 'route' else 'review'


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--fixture', default=str(ROOT / 'benchmarks' / 'support_overescalation_v1.json'))
    p.add_argument('--url', default='http://127.0.0.1:8009')
    p.add_argument('--old-policy', help='path to the earlier support_v2.py for attribution')
    p.add_argument('--output', default=str(ROOT / 'outputs' / 'overescalation-v1.json'))
    args = p.parse_args()
    old = load_old(args.old_policy) if args.old_policy else None
    rows = []
    for case in json.loads(Path(args.fixture).read_text()):
        req = urllib.request.Request(args.url + '/v1/support/decide', data=json.dumps({'ticket': case['ticket']}).encode(), headers={'content-type': 'application/json'})
        with urllib.request.urlopen(req, timeout=120) as r:
            resp = json.load(r)
        decision = resp['decision']
        row = {**case, 'predicted': final(decision), 'reason': decision.get('reason')}
        if old is not None:
            answers = resp['evidence']['answers']
            row['old_policy_predicted'] = final(old.decide(answers, case['ticket']))
        rows.append(row)
    single = [r for r in rows if r['team'] != 'review']
    controls = [r for r in rows if r['team'] == 'review']
    summary = {
        'single_intent_cases': len(single),
        'routed_correctly': sum(r['predicted'] == r['team'] for r in single),
        'unnecessarily_escalated': sum(r['predicted'] == 'review' for r in single),
        'routed_to_wrong_team': sum(r['predicted'] not in ('review', r['team']) for r in single),
        'escalation_reasons': dict(Counter(r['reason'] for r in single if r['predicted'] == 'review')),
        'review_controls': len(controls),
        'review_controls_caught': sum(r['predicted'] == 'review' for r in controls),
    }
    if old is not None:
        summary['escalated_by_old_policy'] = sum(r['old_policy_predicted'] == 'review' for r in single)
        # Live option-order instability comes from the robustness check, which the offline
        # policy replay does not run, so it is not attributable to policy rules.
        summary['escalated_only_by_new_rules'] = [r['id'] for r in single if r['predicted'] == 'review' and r['old_policy_predicted'] != 'review' and r['reason'] != 'option_order_instability']
    report = {'fixture': str(Path(args.fixture).relative_to(ROOT)), 'limitations': '50 authored synthetic tickets written by the policy author before evaluation, evaluated once. Not customer data.', 'summary': summary, 'rows': rows}
    Path(args.output).write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
