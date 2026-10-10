# Product review comprehension comparison

SafeTicket was tested on a different task from support routing: classifying review
sentiment, detecting whether the reviewer recommends the product, and rating
personal satisfaction. Each model received the same three typed questions for
each of 18 English reviews.

| Measure | SafeTicket / Kev backend | Laya English | Laya typed-decisions |
|---|---:|---:|---:|
| Sentiment | 18/18 | 18/18 | 18/18 |
| Recommendation | 17/18 | 14/18 | 16/18 |
| Satisfaction level | 18/18 | 17/18 | 17/18 |
| All three questions correct | **17/18** | 14/18 | 16/18 |
| Individual judgments | **53/54** | 49/54 | 51/54 |

SafeTicket's only miss was a nuanced review that expressed neutral personal opinion
while recommending the product for a limited group. The Laya models also
struggled with mixed personal and general opinions and instruction text inside
reviews. The English Laya model additionally followed the injected instruction
in one review.

The fixture and prompts were written before running any model. The test is
small, synthetic, English-only, and authored for this project, so it supports a
task-specific result rather than a general model ranking. SafeTicket still uses the
Kev model underneath; this result measures the SafeTicket API and decision behavior.

Raw results:

- `outputs/reviews-safeticket.json`
- `outputs/reviews-english.json`
- `outputs/reviews-typed-decisions.json`
