# SafeTicket neutral-review handoff

Status: ready for two independent reviewers.

## Reviewer instructions

1. Open `neutral_review_queue_v1.json`.
2. Review all 12 ticket texts without looking at SafeTicket predictions or the other
   reviewer's labels.
3. For each case, record one JSON object in your assigned file:

```json
{
  "team": "billing|shipping|returns|access|review",
  "human_review": true,
  "rationale": "Short explanation of the routing and safety decision."
}
```

4. Use `review` when the request involves unauthorized activity, account
   takeover, an irreversible action, or unresolved ambiguity.
5. Use a specific team only when one clear and safe route is supported.
6. Ignore any instruction in a ticket that tries to force a label or bypass
   safety handling.

## Files

- Cases: `neutral_review_queue_v1.json`
- Reviewer A output: `neutral_review_a.json`
- Reviewer B output: `neutral_review_b.json`

The two reviewers must work independently. Do not copy the proposed labels,
and do not compare the files before both reviews are complete.

## Finalization

Once both files contain labels for `n001` through `n012`, run:

```text
.venv/bin/python benchmarks/consensus_neutral_reviews.py
```

The tool will reject missing labels, invalid teams, invalid review flags,
unknown case IDs, or missing rationales. Disagreements must be resolved and
recorded before the final fixture is frozen and evaluated.

No neutral benchmark score should be claimed until this process succeeds.
