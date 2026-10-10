"""Replay the current support policy against frozen model outputs.

This isolates policy changes from model/runtime changes. It does not rerun
inference and must not be presented as a fresh model benchmark.
"""
import json
from pathlib import Path

from safeticket.support_v2 import decide


def main():
    rows_by_backend = {}
    for backend in ('kev', 'english', 'typed-decisions'):
        report = json.loads(Path(f'outputs/comparison-{backend}.json').read_text())
        rows = []
        for row in report['rows']:
            decision = decide(row['response']['answers'], row['ticket'])
            final = decision['team'] if decision['action'] == 'route' else 'review'
            rows.append({**row, 'replayed_decision': decision, 'replayed_final': final})
        rows_by_backend[backend] = rows

    summary = {}
    for backend, rows in rows_by_backend.items():
        summary[backend] = {
            'policy_correct': sum(r['replayed_final'] == r['team'] for r in rows),
            'total': len(rows),
            'automatic_routes': sum(r['replayed_final'] != 'review' for r in rows),
            'automatic_errors': sum(r['replayed_final'] != 'review' and r['replayed_final'] != r['team'] for r in rows),
            'required_reviews_caught': sum(r['team'] == 'review' and r['replayed_final'] == 'review' for r in rows),
            'required_reviews': sum(r['team'] == 'review' for r in rows),
            'unnecessary_reviews': sum(r['team'] != 'review' and r['replayed_final'] == 'review' for r in rows),
        }

    output = {
        'method': 'Current support-v2 policy replayed against frozen comparison responses',
        'fresh_inference': False,
        'summary': summary,
        'rows': rows_by_backend,
        'limitations': 'This is a policy-only replay of previously recorded synthetic model outputs. It is not a fresh model benchmark and does not measure latency.',
    }
    Path('outputs/support-policy-replay.json').write_text(json.dumps(output, indent=2) + '\n')
    lines = [
        '# SafeTicket support policy replay',
        '',
        '| Backend | Policy accuracy | Automatic errors | Reviews caught | Unnecessary reviews |',
        '|---|---:|---:|---:|---:|',
    ]
    for backend, s in summary.items():
        label = {'kev': 'SafeTicket / Kev backend', 'english': 'Laya English', 'typed-decisions': 'Laya typed-decisions'}[backend]
        lines.append(f"| {label} | {s['policy_correct']}/{s['total']} | {s['automatic_errors']}/{s['automatic_routes']} | {s['required_reviews_caught']}/{s['required_reviews']} | {s['unnecessary_reviews']} |")
    lines += ['', 'This replay uses frozen outputs; no model inference was performed.']
    Path('outputs/support-policy-replay.md').write_text('\n'.join(lines) + '\n')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
