"""Create a combined benchmark report from the frozen support and review runs."""
import json
from pathlib import Path


def main():
    root = Path('outputs')
    support = {name: json.loads((root / f'comparison-{name}.json').read_text()) for name in ('kev', 'english', 'typed-decisions')}
    reviews = {name: json.loads((root / f'reviews-{name if name != "kev" else "safeticket"}.json').read_text()) for name in ('kev', 'english', 'typed-decisions')}
    replay_path = root / 'support-policy-replay.json'
    replay = json.loads(replay_path.read_text())['summary'] if replay_path.exists() else {}
    rows = []
    for name, label in (('kev', 'SafeTicket / Kev backend'), ('english', 'Laya English'), ('typed-decisions', 'Laya typed-decisions')):
        s = support[name]['summary']
        r = reviews[name]['summary']
        rows.append({'backend': label, 'support_correct': s['policy_correct'], 'support_total': s['total'],
                     'support_automatic_routes': s['automatic_routes'], 'support_automatic_errors': s['automatic_errors'],
                     'support_reviews_caught': s['required_reviews_caught'], 'support_reviews_total': s['required_reviews'],
                     'review_correct': r['all_three_correct'], 'review_total': r['reviews'],
                     'review_individual_correct': r['total_correct'], 'review_individual_total': r['total_questions'],
                     'replay': replay.get(name)})
    report = {'tasks': [{'name':'customer-support routing', 'cases':24, 'questions':'team action under the fixed support-v2 policy', 'source':'comparison-*.json'},
                        {'name':'product-review comprehension', 'cases':18, 'questions':'sentiment, recommendation, satisfaction', 'source':'reviews-*.json'}],
              'results': rows,
              'interpretation': 'SafeTicket / Kev backend scores highest on both frozen synthetic tasks, but this is not a neutral ranking: the prompts and support policy were developed on Kev, and the other backends run under that same policy. The support score includes the same SafeTicket review policy applied to every backend; support automatic-route errors and review coverage are reported separately. The review score counts a case correct only when all three judgments are correct.',
              'limitations': '42 authored English synthetic cases total. Prompts and the support policy were developed on Kev, so this is not a neutral model leaderboard. Cases are not customer data, not independent samples for each question, and not sufficient to establish general superiority. SafeTicket still uses Kev weights. Latencies are excluded because backends use different transports and runtimes.',
              'replay_note': 'Support columns above are the recorded results. The replay table applies the current support-v2 policy (2026-10-10) to the same frozen model outputs with no new inference; policy rules were adjusted after seeing the n12, n14 and n15 failures, so replay results are no longer an untouched test.',
              'artifacts': ['outputs/comparison-kev.json','outputs/comparison-english.json','outputs/comparison-typed-decisions.json','outputs/reviews-safeticket.json','outputs/reviews-english.json','outputs/reviews-typed-decisions.json']}
    (root / 'combined-benchmark.json').write_text(json.dumps(report, indent=2) + '\n')
    lines = ['# Combined SafeTicket benchmark', '', '| Backend | Support action accuracy | Support automatic errors | Support reviews caught | Review cases fully correct | Review individual judgments |', '|---|---:|---:|---:|---:|---:|']
    for r in rows:
        lines.append(f"| {r['backend']} | {r['support_correct']}/{r['support_total']} | {r['support_automatic_errors']}/{r['support_automatic_routes']} | {r['support_reviews_caught']}/{r['support_reviews_total']} | {r['review_correct']}/{r['review_total']} | {r['review_individual_correct']}/{r['review_individual_total']} |")
    if replay:
        lines += ['', '## Current-policy replay (2026-10-10)', '', report['replay_note'], '',
                  '| Backend | Support action accuracy | Support automatic errors | Support reviews caught | Unnecessary reviews |', '|---|---:|---:|---:|---:|']
        for r in rows:
            q = r['replay']
            if q:
                lines.append(f"| {r['backend']} | {q['policy_correct']}/{q['total']} | {q['automatic_errors']}/{q['automatic_routes']} | {q['required_reviews_caught']}/{q['required_reviews']} | {q['unnecessary_reviews']} |")
    lines += ['', report['interpretation'], '', '## Limits', '', report['limitations'], '', 'The complete per-case predictions remain in the JSON artifacts listed above.']
    (root / 'combined-benchmark.md').write_text('\n'.join(lines) + '\n')
    print(json.dumps(rows, indent=2))


if __name__ == '__main__':
    main()
