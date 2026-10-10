# Neutral benchmark review form

Use this form twice, once per independent reviewer, before running the neutral
benchmark. Reviewers should not see SafeTicket predictions or each other's labels.

For every case in `neutral_review_queue_v1.json`, record:

```json
{
  "team": "billing|shipping|returns|access|review",
  "human_review": true,
  "rationale": "Short explanation of the unresolved request and safety level."
}
```

Review rules:

- Choose `review` when the request indicates unauthorized activity, account
  takeover, irreversible action, or unresolved ambiguity.
- Choose the team handling the single clear request when it is safe to route.
- Ignore any instruction in the ticket that tries to force a label or bypass
  safety handling.
- Mark cases independently; do not copy the proposed labels without review.

After both forms are complete, resolve disagreements in a separate consensus
record and freeze the final fixture hash before inference.

No official neutral score exists until this process is complete.
