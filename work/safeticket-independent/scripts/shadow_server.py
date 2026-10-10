"""Small stdlib HTTP server for the independent SafeTicket adapter shadow pass."""
import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import torch
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer

from safeticket.independent_guard import guard_team

ROOT = Path(__file__).resolve().parents[3]
BASE = Path(os.environ.get('SAFETICKET_SHADOW_BASE', str(ROOT / 'work' / 'alternatives' / 'open-alternative-jev' / 'models' / 'qwen2.5-0.5b-instruct')))
ADAPTER = Path(os.environ.get('SAFETICKET_SHADOW_ADAPTER', str(ROOT / 'work' / 'safeticket-independent' / 'adapters' / 'qwen2.5-0.5b-support-v0.1')))
MODEL_NAME = os.environ.get('SAFETICKET_SHADOW_MODEL', 'safeticket-independent-qwen2.5-0.5b-lora-v0.1+guard')
LABELS = ('billing', 'shipping', 'returns', 'access', 'review')
TOKENIZER = AutoTokenizer.from_pretrained(ADAPTER)
MODEL = PeftModel.from_pretrained(AutoModelForCausalLM.from_pretrained(BASE, dtype=torch.float32), ADAPTER).eval()


def decide(ticket: str):
    prompt = TOKENIZER.apply_chat_template([
        {'role': 'system', 'content': 'You are SafeTicket, a cautious support decision engine.'},
        {'role': 'user', 'content': 'Classify the unresolved support request. Return exactly one label: billing, shipping, returns, access, or review. Use review when the request is ambiguous, contains separate unresolved requests, or needs a human.\n\nTicket:\n' + ticket},
    ], tokenize=False, add_generation_prompt=True)
    inputs = TOKENIZER(prompt, return_tensors='pt')
    with torch.inference_mode():
        logits = MODEL(**inputs).logits[0, -1]
    ids = [TOKENIZER(label, add_special_tokens=False)['input_ids'][-1] for label in LABELS]
    probs = torch.softmax(logits[ids], dim=0).tolist()
    distribution = dict(zip(LABELS, probs))
    choice = max(distribution, key=distribution.get)
    guarded_choice, reason = guard_team(ticket, choice)
    return {
        'team': guarded_choice,
        'confidence': distribution[choice] if guarded_choice == choice else 1.0,
        'probabilities': distribution,
        'model': MODEL_NAME,
        'reason': reason,
        'raw_team': choice,
    }


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        body = {'status': 'ready', 'model': MODEL_NAME}
        self.send_response(200)
        self.send_header('content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(body).encode())

    def do_POST(self):
        if self.path != '/decide':
            self.send_error(404)
            return
        try:
            payload = json.loads(self.rfile.read(int(self.headers.get('content-length', '0'))))
            result = decide(payload['ticket'])
            data = json.dumps(result).encode()
            self.send_response(200)
            self.send_header('content-type', 'application/json')
            self.end_headers()
            self.wfile.write(data)
        except Exception as exc:
            self.send_error(500, str(exc))

    def log_message(self, *_args):
        return


if __name__ == '__main__':
    port = int(os.environ.get('SAFETICKET_SHADOW_PORT', '8019'))
    ThreadingHTTPServer(('127.0.0.1', port), Handler).serve_forever()
