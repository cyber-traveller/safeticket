# SafeTicket support policy v2

SafeTicket's live support endpoint now uses a revised routing prompt and separate
checks for unauthorized activity and multiple unresolved requests. Automatic
routing requires probability at least 0.55 and a lead of at least 0.25 over
the runner-up. Both incident checks and routing must allow the decision.
Thresholds are development choices, not calibrated production guarantees.
Whitespace-only tickets are now rejected before inference.

| Fresh synthetic evaluation (24 tickets) | Previous SafeTicket | SafeTicket v2 |
|---|---:|---:|
| Correct final actions | 17 | 19 |
| Automatic routes | 12 | 13 |
| Incorrect automatic routes | 2 | 2 |
| Required reviews caught | 7/9 | 8/9 |
| Unnecessary reviews | 5 | 3 |

The new version improved exact action agreement in this small evaluation,
but did not reduce the number of incorrect automatic routes. It still misses
some multi-team requests and can route according to a resolved problem.
It can also misinterpret denied or historical unauthorized activity.

## Method and evidence

The existing 24-ticket development set was used to select the candidate.
An initial eligibility-classification candidate was rejected because it sent
every ticket to review. The simpler candidate improved development agreement
from 18/24 to 21/24. Its prompts and thresholds were then frozen and compared
against v1 on 24 new authored examples; labels were saved before inference.
No changes were made in response to holdout failures.

Both variants use the same local Kev-0.8B model. V2 asks three questions rather
than two, so no speed improvement is claimed. Evaluation timing is diagnostic
only because shared-state caching can favor the second request. These samples
were authored by the same assistant that built the policy; they are synthetic,
not independent customer data. The small differences do not establish a
statistically reliable improvement on real traffic.

Raw predictions and policy/fixture hashes are in `support-v2-development-b.json`
and `support-v2-holdout.json`. The rejected candidate's development output is
preserved in `support-v2-development.json`.

No model weights were trained or changed. Kev provenance remains in API
responses. V1 remains in `safeticket/support.py`; the active policy is
`safeticket/support_v2.py`.
