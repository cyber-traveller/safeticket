"""Run the isolated Open Alternative to Jev checkpoint on SafeTicket support cases."""
import json
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'work' / 'alternatives' / 'open-alternative-jev'))

from so1 import Choice, Decider  # noqa: E402


def main():
    model_path = os.environ.get(
        'SO1_MODEL',
        str(ROOT / 'work' / 'alternatives' / 'open-alternative-jev' / 'models' / 'qwen2.5-0.5b-instruct'),
    )
    decider = Decider.from_pretrained(model_path, backend='hf')
    questions = [Choice('support team', ['billing', 'shipping', 'returns', 'access', 'review'], name='team')]
    rows = []
    for case in json.loads((ROOT / 'benchmarks' / 'support_challenge_v1.json').read_text()):
        started = time.perf_counter()
        result = decider.decide(case['ticket'], questions)[0]
        rows.append({
            **case,
            'predicted': result.choice,
            'confidence': result.confidence,
            'correct': result.choice == case['team'],
            'latency_ms': (time.perf_counter() - started) * 1000,
        })
    summary = {'correct': sum(row['correct'] for row in rows), 'total': len(rows)}
    summary['accuracy'] = summary['correct'] / summary['total']
    report = {
        'model': model_path,
        'backend': 'transformers-cpu',
        'fixture': 'benchmarks/support_challenge_v1.json',
        'limitations': '12 authored synthetic cases, single local run; not production evidence and not a neutral general leaderboard.',
        'summary': summary,
        'rows': rows,
    }
    out = ROOT / 'outputs' / 'open-alternative-support-challenge.json'
    out.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
