"""Evaluate the independent SafeTicket LoRA prototype on reserved local splits."""
import argparse
import json
import os
from pathlib import Path

import torch
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer

from safeticket.independent_guard import guard_team

ROOT = Path(__file__).resolve().parents[3]
BASE = Path(os.environ.get(
    'SAFETICKET_BASE_MODEL',
    str(ROOT / 'work' / 'alternatives' / 'open-alternative-jev' / 'models' / 'qwen2.5-0.5b-instruct'),
))
ADAPTER = Path(os.environ.get(
    'SAFETICKET_ADAPTER_PATH',
    str(ROOT / 'work' / 'safeticket-independent' / 'adapters' / 'qwen2.5-0.5b-support-v0.1'),
))
LABELS = ('billing', 'shipping', 'returns', 'access', 'review')


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--split', choices=['validation', 'test'], default='test')
    p.add_argument('--guarded', action='store_true', help='apply the narrow deterministic safety guard after the model')
    args = p.parse_args()
    rows = [json.loads(x) for x in (ROOT / 'work' / 'safeticket-independent' / 'data' / f'{args.split}.jsonl').read_text().splitlines() if x]
    tok = AutoTokenizer.from_pretrained(ADAPTER)
    model = PeftModel.from_pretrained(AutoModelForCausalLM.from_pretrained(BASE, dtype=torch.float32), ADAPTER).eval()
    correct = 0
    results = []
    for row in rows:
        prompt = tok.apply_chat_template(row['messages'][:-1], tokenize=False, add_generation_prompt=True)
        inputs = tok(prompt, return_tensors='pt')
        with torch.inference_mode():
            output = model.generate(**inputs, max_new_tokens=6, do_sample=False)
        text = tok.decode(output[0][inputs['input_ids'].shape[1]:], skip_special_tokens=True).lower()
        predicted = next((label for label in LABELS if label in text), 'invalid')
        reason = 'independent_model'
        if args.guarded:
            predicted, reason = guard_team(row['messages'][1]['content'].split('Ticket:\n', 1)[1], predicted)
        ok = predicted == row['messages'][-1]['content']
        correct += ok
        results.append({'source_id': row['source_id'], 'expected': row['messages'][-1]['content'], 'predicted': predicted, 'raw': text, 'guard_reason': reason, 'correct': ok})
    report = {'split': args.split, 'guarded': args.guarded, 'correct': correct, 'total': len(rows), 'accuracy': correct / len(rows), 'results': results}
    out = Path(os.environ.get(
        'SAFETICKET_EVAL_OUT',
        str(ROOT / 'work' / 'safeticket-independent' / f'{args.split}-evaluation.json'),
    ))
    out.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k: report[k] for k in ('split', 'correct', 'total', 'accuracy')}, indent=2))


if __name__ == '__main__':
    main()
