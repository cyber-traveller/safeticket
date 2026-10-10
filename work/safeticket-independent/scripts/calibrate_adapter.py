"""Score independent SafeTicket labels from logits and fit a validation temperature."""
import json
import math
from pathlib import Path

import torch
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer

from safeticket.robustness import brier_score, expected_calibration_error

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / 'work' / 'alternatives' / 'open-alternative-jev' / 'models' / 'qwen2.5-0.5b-instruct'
ADAPTER = ROOT / 'work' / 'safeticket-independent' / 'adapters' / 'qwen2.5-0.5b-support-v0.1'
LABELS = ('billing', 'shipping', 'returns', 'access', 'review')


def load_rows(split):
    return [json.loads(x) for x in (ROOT / 'work' / 'safeticket-independent' / 'data' / f'{split}.jsonl').read_text().splitlines() if x]


def score(model, tokenizer, row):
    prompt = tokenizer.apply_chat_template(row['messages'][:-1], tokenize=False, add_generation_prompt=True)
    inputs = tokenizer(prompt, return_tensors='pt')
    with torch.inference_mode():
        logits = model(**inputs).logits[0, -1]
    ids = [tokenizer(label, add_special_tokens=False)['input_ids'][-1] for label in LABELS]
    values = torch.softmax(logits[ids], dim=0).tolist()
    probs = dict(zip(LABELS, values))
    choice = max(probs, key=probs.get)
    return {'probabilities': probs, 'choice': choice, 'actual': row['messages'][-1]['content']}


def report(rows, scored, temperature=1.0):
    records = []
    brier = []
    for row, item in zip(rows, scored):
        logits = [math.log(max(item['probabilities'][label], 1e-12)) * temperature for label in LABELS]
        exps = [math.exp(x - max(logits)) for x in logits]
        total = sum(exps)
        probs = dict(zip(LABELS, [x / total for x in exps]))
        choice = max(probs, key=probs.get)
        correct = choice == item['actual']
        records.append({'confidence': probs[choice], 'correct': correct})
        brier.append(brier_score(probs, item['actual']))
    return {'accuracy': sum(x['correct'] for x in records) / len(records), 'brier': sum(brier) / len(brier), 'ece': expected_calibration_error(records), 'count': len(records)}


def main():
    tokenizer = AutoTokenizer.from_pretrained(ADAPTER)
    model = PeftModel.from_pretrained(AutoModelForCausalLM.from_pretrained(BASE, dtype=torch.float32), ADAPTER).eval()
    validation = load_rows('validation')
    test = load_rows('test')
    validation_scores = [score(model, tokenizer, row) for row in validation]
    test_scores = [score(model, tokenizer, row) for row in test]
    temperatures = [0.25 + i * 0.05 for i in range(56)]
    best = min(temperatures, key=lambda t: report(validation, validation_scores, t)['brier'])
    result = {'validation_raw': report(validation, validation_scores), 'validation_calibrated': report(validation, validation_scores, best), 'test_raw': report(test, test_scores), 'test_calibrated': report(test, test_scores, best), 'temperature': best, 'label_token_ids': {label: tokenizer(label, add_special_tokens=False)['input_ids'] for label in LABELS}}
    (ROOT / 'work' / 'safeticket-independent' / 'calibration.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
