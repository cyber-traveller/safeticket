"""Measure option-order sensitivity on the pinned Kev backend."""
import json
from pathlib import Path
from urllib.request import Request, urlopen

from safeticket.robustness import option_order_stability
from safeticket.support_v2 import QUESTIONS


def call(payload):
    request = Request('http://127.0.0.1:8008/v1/systemone/permute',
                      data=json.dumps(payload).encode(),
                      headers={'content-type': 'application/json'})
    with urlopen(request, timeout=300) as response:
        return json.load(response)


def main():
    rows = []
    for case in json.loads(Path('benchmarks/laya_comparison_new.json').read_text()):
        response = call({'request': {'state': case['ticket'], 'model': 'kev-latest', 'questions': {'team': QUESTIONS['team']}},
                         'question': 'team', 'n_perm': 2, 'seed': 0})
        summary = option_order_stability(response.get('runs', []))
        rows.append({'id': case['id'], 'expected': case['team'], **summary, 'raw': response})
    result = {
        'backend': 'jaredpalmer/kev-0.8b@v1.0',
        'permutations': 2,
        'cases': len(rows),
        'unstable_cases': sum(not row['argmax_stable'] for row in rows),
        'max_spread': max((row['max_probability_spread'] for row in rows), default=0.0),
        'rows': rows,
        'limitations': '24 synthetic tickets; two option orders; diagnostic robustness audit, not an accuracy benchmark.',
    }
    Path('outputs/option-stability.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({key: result[key] for key in ('cases', 'unstable_cases', 'max_spread')}, indent=2))


if __name__ == '__main__':
    main()
