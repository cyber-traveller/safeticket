"""Small, model-agnostic robustness and calibration utilities for SafeTicket."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from math import isfinite


def option_order_stability(runs: Iterable[Mapping]) -> dict:
    """Summarize repeated choice outputs returned under different option orders."""
    runs = list(runs)
    choices = [run.get("choice") for run in runs]
    probability_maps = [run.get("probabilities", {}) for run in runs]
    keys = set().union(*(probs.keys() for probs in probability_maps)) if probability_maps else set()
    spread = {
        key: max((float(probs.get(key, 0.0)) for probs in probability_maps), default=0.0)
        - min((float(probs.get(key, 0.0)) for probs in probability_maps), default=0.0)
        for key in keys
    }
    return {
        "runs": len(runs),
        "argmax_stable": len(set(choices)) <= 1 if choices else False,
        "max_probability_spread": max(spread.values(), default=0.0),
        "spread": spread,
    }


def brier_score(probabilities: Mapping[str, float], actual: str) -> float:
    """Multiclass Brier score for one probability distribution."""
    if actual not in probabilities or not probabilities:
        raise ValueError("actual must be one of the probability keys")
    values = list(probabilities.values())
    if not all(type(value) in (int, float) and isfinite(value) and 0 <= value <= 1 for value in values):
        raise ValueError("probabilities must be finite numbers between 0 and 1")
    return sum((value - (1.0 if key == actual else 0.0)) ** 2 for key, value in probabilities.items())


def expected_calibration_error(records: Iterable[Mapping], bins: int = 10) -> float:
    """Compute confidence ECE from records with ``confidence`` and ``correct``."""
    if bins < 1:
        raise ValueError("bins must be positive")
    records = list(records)
    if not records:
        return 0.0
    total = len(records)
    error = 0.0
    for index in range(bins):
        lower = index / bins
        upper = (index + 1) / bins
        bucket = [record for record in records if lower <= record["confidence"] < upper or (index == bins - 1 and record["confidence"] == 1)]
        if bucket:
            confidence = sum(record["confidence"] for record in bucket) / len(bucket)
            accuracy = sum(bool(record["correct"]) for record in bucket) / len(bucket)
            error += len(bucket) / total * abs(confidence - accuracy)
    return error
