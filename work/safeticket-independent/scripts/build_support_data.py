"""Build an independent SafeTicket support-training split from labeled local fixtures.

Training uses only authored labels. The holdout and adversarial fixtures remain
unseen by this script and are reserved for evaluation.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'work' / 'safeticket-independent' / 'data'

INSTRUCTIONS = (
    'Classify the unresolved support request. Return exactly one label: '
    'billing, shipping, returns, access, or review. Use review when the request '
    'is ambiguous, contains separate unresolved requests, or needs a human.'
)


def row(case):
    return {
        'messages': [
            {'role': 'system', 'content': 'You are SafeTicket, a cautious support decision engine.'},
            {'role': 'user', 'content': f'{INSTRUCTIONS}\n\nTicket:\n{case["ticket"]}'},
            {'role': 'assistant', 'content': case['team']},
        ],
        'source_fixture': case.get('_source'),
        'source_id': case['id'],
    }


def load(name):
    cases = json.loads((ROOT / 'benchmarks' / name).read_text())
    for case in cases:
        case['_source'] = name
    return cases


def augmented_cases():
    templates = {
        'billing': [
            'Please send a receipt for my order.',
            'I need an invoice for the payment.',
            'The same purchase appears twice on my statement.',
            'Can you explain this charge on my bill?',
            'Please correct the billing address on the invoice.',
            'I need a copy of the payment confirmation.',
            'This is a duplicate payment; route the charge question to billing.',
        ],
        'shipping': [
            'Where is my package right now?',
            'Please check the delivery status of my order.',
            'The parcel has not arrived yet.',
            'Can you tell me when the shipment will arrive?',
            'I need tracking information for this order.',
            'The courier says the delivery is delayed.',
        ],
        'returns': [
            'I want to return the item I received.',
            'Please arrange an exchange for a different size.',
            'How do I send this product back?',
            'The item is defective and I want a replacement.',
            'I changed my mind and would like to return this purchase.',
            'Please start a return for the damaged product.',
        ],
        'access': [
            'I cannot sign in to my account.',
            'Please help me reset my forgotten password.',
            'My login is locked after too many attempts.',
            'I need to regain access to my account.',
            'The sign-in code is not working.',
            'Please help unlock my account.',
        ],
        'review': [
            'I need help with two unrelated problems in one message.',
            'I am not sure which team should handle this request.',
            'Please investigate this complicated issue and advise me.',
            'The request is unclear because several things went wrong.',
            'I need a human to review the situation.',
            'There are separate account and order problems to resolve.',
            'A delivery issue and a product issue need different teams.',
            'An account concern and an order concern are both still unresolved.',
            'The message contains two requests and should be reviewed by a human.',
        ],
    }
    return [
        {'id': f'aug-{label}-{i}', 'team': label, 'ticket': text, '_source': 'authored_templates'}
        for label, texts in templates.items() for i, text in enumerate(texts)
    ]


def main():
    train = load('support_cases.json') + load('support_fresh.json') + augmented_cases()
    val = load('support_holdout_v2.json')
    test = load('support_adversarial_v1.json')
    for name, cases in [('train', train), ('validation', val), ('test', test)]:
        (OUT / f'{name}.jsonl').write_text('\n'.join(json.dumps(row(c)) for c in cases) + '\n')
    (OUT / 'provenance.json').write_text(json.dumps({
        'base_model': 'Qwen/Qwen2.5-0.5B-Instruct',
        'base_model_license': 'Apache-2.0',
        'training_sources': ['benchmarks/support_cases.json', 'benchmarks/support_fresh.json', 'authored_templates in this script'],
        'reserved_evaluation_sources': ['benchmarks/support_holdout_v2.json', 'benchmarks/support_adversarial_v1.json'],
        'labeling': 'authored local labels; no Kev predictions used as labels',
    }, indent=2) + '\n')
    print(json.dumps({'train': len(train), 'validation': len(val), 'test_reserved': len(test)}, indent=2))


if __name__ == '__main__':
    main()
