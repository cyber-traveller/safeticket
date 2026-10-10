"""Run the fixed SafeTicket benchmark against any System One-compatible endpoint.

The endpoint, model, and optional bearer token are supplied through arguments
or environment variables. Secrets are never written to the report.
"""
import argparse
import json
import os
from pathlib import Path

from safeticket.client import SystemOneClient
from safeticket.support_v2 import QUESTIONS as SUPPORT_QUESTIONS, decide
from benchmarks.evaluate_reviews import QUESTIONS as REVIEW_QUESTIONS


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--base-url', default=os.environ.get('SYSTEMONE_BASE_URL'))
    parser.add_argument('--model', default=os.environ.get('SYSTEMONE_MODEL', 'jev-latest'))
    parser.add_argument('--output', default='outputs/systemone-comparison.json')
    args = parser.parse_args()
    if not args.base_url:
        parser.error('--base-url or SYSTEMONE_BASE_URL is required')

    token = os.environ.get('SYSTEMONE_API_KEY')
    headers = {'authorization': f'Bearer {token}'} if token else {}
    rows = {'support': [], 'reviews': []}
    with SystemOneClient(args.base_url, headers=headers) as client:
        for case in json.loads(Path('benchmarks/laya_comparison_new.json').read_text()):
            response = client.system_one({'state': case['ticket'], 'model': args.model, 'questions': SUPPORT_QUESTIONS})
            decision = decide(response['answers'], case['ticket'])
            final = decision['team'] if decision['action'] == 'route' else 'review'
            rows['support'].append({'id': case['id'], 'expected': case['team'], 'prediction': final,
                                    'correct': final == case['team'], 'decision': decision, 'response': response})
        for case in json.loads(Path('benchmarks/reviews.json').read_text()):
            response = client.system_one({'state': case['text'], 'model': args.model, 'questions': REVIEW_QUESTIONS})
            answers = response['answers']
            prediction = {'sentiment': answers['sentiment']['choice'], 'recommend': answers['recommend']['noul'] >= .5,
                          'level': int(max(answers['level']['probabilities'], key=answers['level']['probabilities'].get))}
            rows['reviews'].append({'expected': case, 'prediction': prediction,
                                    'correct': {key: prediction[key] == case[key] for key in prediction},
                                    'response': response})

    support = rows['support']
    review = rows['reviews']
    report = {
        'endpoint': args.base_url,
        'model': args.model,
        'fresh_inference': True,
        'summary': {
            'support_correct': sum(row['correct'] for row in support),
            'support_total': len(support),
            'support_automatic_errors': sum(row['prediction'] != 'review' and not row['correct'] for row in support),
            'support_reviews_caught': sum(row['expected'] == 'review' and row['prediction'] == 'review' for row in support),
            'support_reviews_total': sum(row['expected'] == 'review' for row in support),
            'review_cases_fully_correct': sum(all(row['correct'].values()) for row in review),
            'review_cases_total': len(review),
            'review_individual_correct': sum(sum(row['correct'].values()) for row in review),
            'review_individual_total': 3 * len(review),
        },
        'rows': rows,
        'limitations': 'Synthetic fixed fixtures; not production evidence or a general superiority claim. Questions and support policy were developed on Kev.',
    }
    Path(args.output).write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report['summary'], indent=2))


if __name__ == '__main__':
    main()
