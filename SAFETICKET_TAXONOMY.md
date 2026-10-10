# SafeTicket Domain-Aware Taxonomy Proposal

Status: design only — not connected to the live API.

## Why this is needed

The current support API exposes five coarse teams:

`billing`, `shipping`, `returns`, `access`, and `review`.

That works well for the current support-routing task, but it collapses many
legitimate banking intents into `review`. BANKING77 contains fine-grained
intents such as card arrival, transfer status, cash withdrawal, identity
verification, compromised cards, and top-up failures. A broader taxonomy is
needed before SafeTicket can claim general decision-making strength.

## Proposed first-level domains

| Domain | Example intents | Safety posture |
|---|---|---|
| card_lifecycle | arrival, delivery estimate, activation, expiry, replacement | route when specific; review if ownership is unclear |
| card_usage | card not working, contactless, acceptance, linking | route clear troubleshooting; review suspected compromise |
| payments | declined, pending, reversed, duplicate, fees, exchange rate | route ordinary issues; review unauthorized activity |
| cash | ATM fees, declined withdrawal, wrong amount, cash not received | route ordinary issues; review unrecognized withdrawal |
| transfers | pending, failed, delayed, recipient not received, beneficiary | route clear status questions; review mixed requests |
| topups | card top-up, limits, pending, failed, reversed, fees | route ordinary top-up issues; review suspicious activity |
| refunds | request refund, refund missing, payment reversal | route clear refund requests; review mixed or disputed cases |
| identity_access | passcode, PIN, verification, account access, personal details | route ordinary access recovery; review takeover signals |
| security | compromised card, unrecognized payment, stolen card or phone | human review by default |
| account_policy | age, country support, account termination, supported currencies | route informational questions |
| review | ambiguous, multi-intent, unsupported, or high-risk requests | human review |

## Decision contract

The future domain-aware endpoint should return:

```json
{
  "action": "route | human_review",
  "domain": "payments",
  "intent": "transaction_charged_twice",
  "confidence": 0.0,
  "reason": "...",
  "safety": {
    "requires_human": false,
    "signals": []
  }
}
```

The five-team endpoint remains stable for existing clients. Domain-aware
classification should be additive and versioned rather than silently changing
the meaning of existing team labels.

## Evaluation plan

1. Use the BANKING77 training split only to refine this mapping and prompt.
2. Freeze the taxonomy and mapping before touching the official test split.
3. Evaluate one or more examples from every intent.
4. Report exact intent accuracy, domain accuracy, unsafe automatic routes,
   review recall, and latency.
5. Compare the broader taxonomy against the current five-team baseline.
6. Keep the new endpoint experimental until it passes the promotion gate.

## Non-goals

- This proposal does not claim that SafeTicket currently supports all listed intents.
- It does not change the live Kev-backed endpoint.
- It does not authorize publishing or redistribution of BANKING77 files.
- It does not replace human review for security or ambiguous cases.
