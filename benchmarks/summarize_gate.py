"""Write the current paired SafeTicket comparison gate from recorded results."""
import json
from pathlib import Path


def load(path):
    return json.loads(Path(path).read_text())


ADAPTERS = (
    ('qwen2.5-0.5b-support-v0.1', 'Qwen2.5-0.5B v0.1 (gate adapter)'),
    ('qwen2.5-0.5b-support-v0.2', 'Qwen2.5-0.5B v0.2'),
    ('qwen2.5-0.5b-support-v0.3', 'Qwen2.5-0.5B v0.3'),
    ('qwen2.5-1.5b-support-v0.1', 'Qwen2.5-1.5B v0.1'),
    ('qwen2.5-1.5b-support-v0.2', 'Qwen2.5-1.5B v0.2 (shadow server)'),
    ('qwen2.5-1.5b-support-v0.3-safety', 'Qwen2.5-1.5B v0.3-safety'),
    ('qwen2.5-1.5b-support-v0.4-safety-1e', 'Qwen2.5-1.5B v0.4-safety-1e'),
)
RERUN = Path('outputs/independent-rerun-2026-10-10')


def adapter_table():
    """Per-adapter validation/test scores from the 2026-10-10 re-run; the v0.1 0.5B adapter uses the recorded gate files."""
    rows = []
    for key, label in ADAPTERS:
        scores = {}
        for split in ('validation', 'test'):
            for mode in ('raw', 'guarded'):
                if key == 'qwen2.5-0.5b-support-v0.1':
                    path = RERUN / f'{split}-{mode}.json'
                else:
                    path = RERUN / 'adapters' / f'{key}-{split}-{mode}.json'
                if not path.exists():
                    scores[f'{split}_{mode}'] = None
                    continue
                data = load(path)
                scores[f'{split}_{mode}'] = f"{data['correct']}/{data['total']}"
        rows.append({'adapter': label, **scores})
    return rows


def main():
    live = load('outputs/safeticket-holdout-v2.json')['summary']
    adversarial = load('outputs/safeticket-adversarial-v1.json')['summary']
    independent = load('work/safeticket-independent/test-evaluation.json')
    validation = load('work/safeticket-independent/validation-evaluation.json')
    guarded = load('work/safeticket-independent/test-evaluation-guarded.json')
    guarded_validation = load('work/safeticket-independent/validation-evaluation-guarded.json')
    open_alternative = load('outputs/open-alternative-support-challenge.json')['summary']
    jevos = load('outputs/jevos-comparison.json')['summary']
    report = {
        'fixtures': {
            'support_holdout_v2': live,
            'support_adversarial_v1': adversarial,
            'independent_adapter_validation': {'correct': validation['correct'], 'total': validation['total']},
            'independent_adapter_adversarial': {'correct': independent['correct'], 'total': independent['total']},
            'independent_guarded_validation': {'correct': guarded_validation['correct'], 'total': guarded_validation['total']},
            'independent_guarded_adversarial': {'correct': guarded['correct'], 'total': guarded['total']},
            'open_alternative_support_challenge': open_alternative,
        },
        'comparators': {
            'live_safeticket_policy': {'holdout': f"{live['correct']}/{live['total']}", 'adversarial': f"{adversarial['correct']}/{adversarial['total']}", 'automatic_errors_holdout': live['automatic_errors']},
            'independent_safeticket_adapter': {'validation': f"{validation['correct']}/{validation['total']}", 'adversarial': f"{independent['correct']}/{independent['total']}"},
            'independent_safeticket_guarded_adapter': {'validation': f"{guarded_validation['correct']}/{guarded_validation['total']}", 'adversarial': f"{guarded['correct']}/{guarded['total']}"},
            'open_alternative': {'challenge': f"{open_alternative['correct']}/{open_alternative['total']}"},
            'jevos': jevos,
            'laya': 'See outputs/combined-benchmark.json; Laya English and typed-decisions are evaluated on the original 24-case support fixture.',
        },
        'independent_adapter_versions': adapter_table(),
        'gate': {
            'live_policy_passes_current_safety_gate': live['correct'] == live['total'] and live['automatic_errors'] == 0 and live['required_reviews_caught'] == live['required_reviews'],
            'independent_adapter_ready_to_replace_live': independent['correct'] == independent['total'] and validation['correct'] == validation['total'],
            'independent_guarded_path_passes_current_fixtures': guarded['correct'] == guarded['total'] and guarded_validation['correct'] == guarded_validation['total'],
        },
        'limitations': 'Authored synthetic fixtures, different model artifacts and runtimes, no production data, and no general superiority claim. The live SafeTicket policy still uses Kev weights.',
    }
    Path('outputs/safeticket-benchmark-gate.json').write_text(json.dumps(report, indent=2) + '\n')
    lines = ['# SafeTicket benchmark gate', '', '| System | Holdout | Adversarial | Replacement status |', '|---|---:|---:|---|', f"| Live SafeTicket policy | {live['correct']}/{live['total']} | {adversarial['correct']}/{adversarial['total']} | Passes current safety gate |", f"| Independent SafeTicket adapter | {validation['correct']}/{validation['total']} validation | {independent['correct']}/{independent['total']} | Raw model not ready |", f"| Independent SafeTicket + safety guard | {guarded_validation['correct']}/{guarded_validation['total']} | {guarded['correct']}/{guarded['total']} | Passes current fixtures; shadow only |", f"| Open Alternative 0.5B | not run | {open_alternative['correct']}/{open_alternative['total']} challenge | Rejected for support routing |", f"| jevos | {jevos['support_correct']}/{jevos['support_total']} support | not run on this adversarial fixture | Comparator only |", '| Laya | See combined benchmark | See combined benchmark | Comparator only |', '', report['limitations']]
    table = ['', '## Independent adapter versions (re-run 2026-10-10)', '', '| Adapter | Validation raw | Validation guarded | Test raw | Test guarded |', '|---|---:|---:|---:|---:|']
    for row in report['independent_adapter_versions']:
        table.append(f"| {row['adapter']} | {row['validation_raw']} | {row['validation_guarded']} | {row['test_raw']} | {row['test_guarded']} |")
    lines[-2:-2] = table
    Path('outputs/safeticket-benchmark-gate.md').write_text('\n'.join(lines) + '\n')
    print(json.dumps(report['gate'], indent=2))


if __name__ == '__main__':
    main()
