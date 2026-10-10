# Neutral SafeTicket evaluation protocol

Status: preparation only; no neutral score has been claimed.

## Purpose

Measure SafeTicket on decisions that were not written from the existing Kev policy
fixtures. The evaluation must separate routing accuracy, safe abstention, and
latency.

## Required review process

1. Draft cases across at least six domains: payments, access, delivery,
   returns, security, and general policy.
2. Have two reviewers independently assign the intended team and whether
   human review is required.
3. Resolve disagreements before inference and record the final label with a
   short rationale.
4. Freeze the fixture hash before running SafeTicket or any comparator.
5. Keep the labels and prompts separate from implementation-tuning notes.

## Reported metrics

- Final-action accuracy.
- Automatic-route accuracy, excluding human-review cases.
- Required-review recall.
- Abstention rate.
- Median and p95 latency.
- Error categories, especially security and prompt-injection cases.

## Publication rule

This protocol does not authorize publishing results or model artifacts. Any
dataset licenses, source attribution, and model-weight terms must be recorded
before external release.
