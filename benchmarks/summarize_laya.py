"""Summarize all completed backend runs without changing decisions or thresholds."""
import json
import random
from pathlib import Path


def interval(differences):
    rng = random.Random(731)
    samples = sorted(sum(rng.choices(differences, k=len(differences)))/len(differences) for _ in range(5000))
    return [samples[124], samples[4874]]


def main():
    names = ['kev', 'english', 'typed-decisions']
    reports = {n:json.loads(Path(f'outputs/comparison-{n}.json').read_text()) for n in names}
    reference = reports['kev']
    for r in reports.values():
        assert r['metadata']['fixture_sha256'] == reference['metadata']['fixture_sha256']
        assert r['metadata']['questions'] == reference['metadata']['questions']
        assert r['metadata']['policy_sha256'] == reference['metadata']['policy_sha256']
        assert [x['id'] for x in r['rows']] == [x['id'] for x in reference['rows']]
    result = {'summaries':{n:r['summary'] for n,r in reports.items()}, 'paired_policy_accuracy_difference':{}, 'raw_routing_at_matched_coverage':{}}
    for n in names[1:]:
        diffs = [int(a['final']==a['team']) - int(b['final']==b['team']) for a,b in zip(reference['rows'], reports[n]['rows'])]
        result['paired_policy_accuracy_difference'][n] = {'safeticket_minus_laya':sum(diffs)/len(diffs), 'bootstrap_95_percent_interval':interval(diffs)}
    # Diagnostic ranking comparison; no ground-truth-based threshold fitting.
    for n, r in reports.items():
        eligible = [x for x in r['rows'] if x['raw'] != 'review']
        eligible.sort(key=lambda x: (-x['response']['answers']['team']['probabilities'][x['raw']], x['id']))
        result['raw_routing_at_matched_coverage'][n] = {
            str(k): {'routes':k, 'errors':sum(x['raw'] != x['team'] for x in eligible[:k])} if len(eligible)>=k else None
            for k in (6,12)}
    Path('outputs/laya-comparison-summary.json').write_text(json.dumps(result, indent=2)+'\n')
    lines = ['# SafeTicket versus Laya: initial local comparison', '',
             'All three backends received the same 24 newly authored synthetic tickets and the same questions. The SafeTicket support-v2 policy was also applied identically to all three. No tuning was performed on this test set.', '',
             '| Measure | SafeTicket / Kev-0.8B | Laya English | Laya typed-decisions |',
             '|---|---:|---:|---:|']
    for label, key in [('Raw team answers correct','raw_correct'), ('Correct actions with identical policy','policy_correct'), ('Automatic routes','automatic_routes'), ('Incorrect automatic routes','automatic_errors'), ('Required reviews caught (of 9)','required_reviews_caught'), ('Unnecessary reviews','unnecessary_reviews')]:
        lines.append('| '+label+' | '+' | '.join(str(reports[n]['summary'][key]) for n in names)+' |')
    lines += ['', '## Limits', '',
              'This is a small synthetic, English support-only comparison. The prompts and policy were developed on Kev, so this fixed-prompt experiment favors SafeTicket. It is not an equal-budget tuning comparison or proof of general superiority. A paired bootstrap interval is provided in the JSON; it describes uncertainty on these authored cases, not real-world representativeness.', '',
              'Both Laya checkpoints use the pinned Hub revision 7b928d828b7b0e022f929d9bd2e44165aa270148 and verified SHA-256 weights. Runtime: Laya 0.4.1. Full configurations, input-truncation checks, responses and hashes are in the per-backend JSON files.', '',
              'Laya runs through its local SDK and Kev through HTTP, with different dtypes and caching. Diagnostic times must not be used as a latency ranking. No model weights were trained or changed. SafeTicket still uses Kev weights.', '',
              'The JSON summary also reports raw routing errors at matched 25% and 50% coverage, without selecting thresholds using the test labels. Human review is not counted as an automatic correct route.']
    Path('outputs/laya-comparison-report.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
