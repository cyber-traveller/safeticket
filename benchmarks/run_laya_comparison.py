"""Pinned local-backend quality comparison, with identical SafeTicket questions/policy.

Run each Laya backend in a separate process. This is an initial fixed-prompt
comparison, not equal-budget model-specific tuning or a production benchmark.
"""
import argparse
import hashlib
import importlib.metadata
import json
import platform
import statistics
import time
from datetime import datetime, timezone
from pathlib import Path

from safeticket.support_v2 import QUESTIONS, decide
from safeticket.client import SystemOneClient
from benchmarks.fetch_laya import HASHES, REVISION


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--backend', choices=['kev', 'english', 'typed-decisions'], required=True)
    args = parser.parse_args()
    fixture = Path('benchmarks/laya_comparison_new.json')
    cases = json.loads(fixture.read_text())
    meta = {'backend':args.backend, 'model_revision':REVISION if args.backend != 'kev' else 'see server metadata',
            'python':platform.python_version(), 'platform':platform.platform(),
            'questions':QUESTIONS, 'fixture_sha256':hashlib.sha256(fixture.read_bytes()).hexdigest(),
            'policy_sha256':hashlib.sha256(Path('safeticket/support_v2.py').read_bytes()).hexdigest(),
            'measured_at':datetime.now(timezone.utc).isoformat()}
    if args.backend == 'kev':
        client = SystemOneClient('http://127.0.0.1:8008')
        predict = lambda ticket: client.system_one({'state':ticket, 'model':'kev-latest', 'questions':QUESTIONS})
    else:
        import laya
        import torch
        from laya.common import build_head, render_options
        folder = Path('work/laya-models')
        key = 'model.safetensors'
        if args.backend == 'typed-decisions':
            folder /= 'typed-decisions'
            key = 'typed-decisions/' + key
        with (folder/'model.safetensors').open('rb') as f:
            digest = hashlib.file_digest(f, 'sha256').hexdigest()
        assert digest == HASHES[key]
        agent = laya.load(str(folder.resolve()), device='mps', backend='eager')
        # Check the actual tokenizer/renderer preserves all instructions and options.
        audits = []
        for q in QUESTIONS.values():
            internal = agent._to_internal(q)
            head, markers, stats = build_head(agent.tok, internal, 384)
            full, fullmarkers, fullstats = build_head(agent.tok, internal, 8192)
            assert head == full and markers == fullmarkers, 'Question head truncated'
            assert stats['options_distinct'] == len(render_options(internal))
            audits.append({'head_tokens':len(head), 'options':stats})
        meta.update({'versions':{p:importlib.metadata.version(p) for p in ['laya','torch','transformers','huggingface-hub']},
                     'weight_sha256':digest, 'device':str(agent.device), 'dtype':str(agent.dtype_for(len(QUESTIONS))),
                     'config':agent.cfg, 'question_audit':audits, 'max_len':512, 'head_max_len':384})
        def predict(ticket):
            r = agent.system_one(ticket, QUESTIONS, max_len=512, head_max_len=384)
            if r.get('usage', {}).get('truncated') or r.get('usage', {}).get('options'):
                raise RuntimeError('Input truncation or option collapse: '+str(r['usage']))
            return r
    predict('Please send a receipt for my purchase.')  # excluded model warmup
    rows = []
    for case in cases:
        start = time.perf_counter()
        response = predict(case['ticket'])
        elapsed = (time.perf_counter()-start)*1000
        answers = response['answers']
        decision = decide(answers, case['ticket'])
        final = decision['team'] if decision['action'] == 'route' else 'review'
        rows.append({**case, 'raw':answers['team']['choice'], 'final':final,
                     'decision':decision, 'response':response, 'elapsed_ms':elapsed})
    summary = {'total':len(rows), 'raw_correct':sum(r['raw']==r['team'] for r in rows),
               'policy_correct':sum(r['final']==r['team'] for r in rows),
               'automatic_routes':sum(r['final']!='review' for r in rows),
               'automatic_errors':sum(r['final']!='review' and r['final']!=r['team'] for r in rows),
               'required_reviews':sum(r['team']=='review' for r in rows),
               'required_reviews_caught':sum(r['team']=='review' and r['final']=='review' for r in rows),
               'unnecessary_reviews':sum(r['team']!='review' and r['final']=='review' for r in rows),
               'diagnostic_median_ms':statistics.median(r['elapsed_ms'] for r in rows)}
    report = {'metadata':meta, 'summary':summary, 'rows':rows,
              'limitations':'24 synthetic tickets authored before inference. Same prompts favor SafeTicket because developed on Kev. Same uncalibrated policy on all. Laya direct SDK vs Kev HTTP: timings are diagnostic, not a fair latency ranking. No production or statistical superiority claim.'}
    Path(f'outputs/comparison-{args.backend}.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(summary, indent=2), flush=True)


if __name__ == '__main__':
    main()
