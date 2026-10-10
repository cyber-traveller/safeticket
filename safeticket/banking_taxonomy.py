"""Experimental domain-aware banking taxonomy.

This is additive and intentionally separate from the five-team support policy.
It is a conservative lexical baseline for taxonomy development, not a trained
77-intent model.
"""
from __future__ import annotations

import re


def legacy_team(domain: str) -> str:
    """Map a fine-grained domain to the existing five-team contract."""
    return {
        "card_lifecycle": "shipping",
        "card_usage": "access",
        "refunds": "returns",
        "identity_access": "access",
        "security": "review",
        "review": "review",
    }.get(domain, "billing")


def _has(text: str, pattern: str) -> bool:
    return bool(re.search(pattern, text, re.I))


def classify(ticket: str) -> dict:
    text = ticket if isinstance(ticket, str) else ""
    if not text.strip():
        return {"action": "human_review", "domain": "review", "intent": "invalid_request", "confidence": 1.0, "reason": "empty_request", "safety": {"requires_human": True, "signals": ["empty_request"]}}

    security = []
    if _has(text, r"\b(?:unauthori[sz]ed|not mine|not made by me|did not make|didn.t perform|don.t recognize|do not recognize|strange|unfamiliar|without my permission|activity on my card|someone is using.*card|someone.*(?:took|withdrew|used).*\b(?:cash|money|card)|transactions.*remember|stolen|compromised|stranger|someone else|unknown person)\b"):
        security.append("possible_unauthorized_activity")
    if _has(text, r"\b(?:accessed|signed into|changed my (?:email|phone|recovery)|broke into|atm.*(?:took|stole|swallowed)|(?:took|stole|swallowed).*atm)\b"):
        security.append("possible_account_takeover")
    if security:
        return {"action": "human_review", "domain": "security", "intent": "security_incident", "confidence": 0.99, "reason": "security_signal", "safety": {"requires_human": True, "signals": security}}

    # Policy-sensitive card and wallet operations are deliberately reviewed.
    if _has(text, r"\b(?:activate|activation)\b") and _has(text, r"\bcard\b"):
        return {"action": "human_review", "domain": "review", "intent": "activate_card", "confidence": 0.90, "reason": "card_activation_review", "safety": {"requires_human": True, "signals": ["card_state_change"]}}
    if _has(text, r"\b(?:apple\s*pay|google\s*pay|apple watch|google wallet)\b"):
        return {"action": "human_review", "domain": "review", "intent": "mobile_wallet_support", "confidence": 0.88, "reason": "mobile_wallet_policy", "safety": {"requires_human": True, "signals": ["wallet_policy"]}}
    if _has(text, r"\b(?:change|unlock|blocked|failed)\b") and _has(text, r"\bpin\b"):
        return {"action": "route", "domain": "identity_access", "intent": "pin_support", "confidence": 0.84, "reason": "pin_support_signal", "safety": {"requires_human": False, "signals": []}}
    if _has(text, r"\b(?:physical|spare|additional|extra|another) card\b") and _has(text, r"\b(?:get|order|receive|another|new|cost|price|obtain)\b"):
        return {"action": "human_review", "domain": "review", "intent": "physical_card_order", "confidence": 0.88, "reason": "physical_card_policy", "safety": {"requires_human": True, "signals": ["card_order"]}}
    if _has(text, r"\bcard\b") and _has(text, r"\b(?:expire|expired|expiry)\b"):
        return {"action": "human_review", "domain": "review", "intent": "card_expiry", "confidence": 0.88, "reason": "card_expiry_policy", "safety": {"requires_human": True, "signals": ["card_replacement"]}}
    if _has(text, r"\bcard\b") and _has(text, r"\b(?:sent|shipped|available|get)\b") and _has(text, r"\b(?:China|US|UK|USA|Canada|Australia|country|abroad)\b"):
        return {"action": "human_review", "domain": "review", "intent": "card_country_support", "confidence": 0.80, "reason": "card_country_policy", "safety": {"requires_human": True, "signals": ["eligibility_policy"]}}
    if _has(text, r"\b(?:exchange|convert)\b") and _has(text, r"\b(?:currency|currencies|gbp|usd|eur|app)\b"):
        return {"action": "human_review", "domain": "review", "intent": "exchange_support", "confidence": 0.80, "reason": "exchange_policy", "safety": {"requires_human": True, "signals": ["currency_policy"]}}
    if _has(text, r"\b(?:which|what|any|all|do all)\b.*\b(?:atm|cash machine)s?\b"):
        return {"action": "human_review", "domain": "review", "intent": "atm_support", "confidence": 0.82, "reason": "atm_policy_review", "safety": {"requires_human": True, "signals": ["policy_specific"]}}
    if not _has(text, r"\b(?:top[- ]?up|topping up|cash|withdraw\w*|exchange|currency|currencies)\b") and ((_has(text, r"\b(?:country|countries)\b") or _has(text, r"\b(?:US|UK|USA|Canada|Australia)\b")) and _has(text, r"\b(?:support|live|card|get)\b")):
        return {"action": "human_review", "domain": "review", "intent": "country_support", "confidence": 0.80, "reason": "country_policy", "safety": {"requires_human": True, "signals": ["eligibility_policy"]}}
    if _has(text, r"\b(?:physical|spare|additional|extra) card\b") and _has(text, r"\bpin\b"):
        return {"action": "human_review", "domain": "review", "intent": "physical_card_support", "confidence": 0.84, "reason": "physical_card_policy", "safety": {"requires_human": True, "signals": ["card_policy"]}}
    if _has(text, r"\bcard\b") and _has(text, r"\bpin\b") and _has(text, r"\b(?:get|have|sent|receive|where|what do)\b"):
        return {"action": "human_review", "domain": "review", "intent": "card_pin_support", "confidence": 0.82, "reason": "card_pin_policy", "safety": {"requires_human": True, "signals": ["card_policy"]}}

    if (_has(text, r"\b(?:cheque|check|cash) deposit\b") or _has(text, r"\bcash I deposited\b") or _has(text, r"\b(?:cheque|check)\b.*\b(?:balance|appear|showing)\b")) and _has(text, r"\b(?:balance|waiting|pending|updated|showing|appear|taking.*long|deposited)\b"):
        return {"action": "route", "domain": "payments", "intent": "cash_deposit_balance", "confidence": 0.82, "reason": "deposit_balance_signal", "safety": {"requires_human": False, "signals": []}}
    if (_has(text, r"\b(?:declined|denied|refused)\b") or _has(text, r"\b(?:won.t let me|can.t get)\b")) and _has(text, r"\b(?:cash withdrawal|withdraw|cash machine|atm|money out)\b"):
        return {"action": "route", "domain": "cash", "intent": "declined_cash_withdrawal", "confidence": 0.86, "reason": "declined_cash_signal", "safety": {"requires_human": False, "signals": []}}
    if _has(text, r"\b(?:pending|failed|denied|declined)\b") and _has(text, r"\b(?:top[- ]?up|topped up|topping up)\b"):
        return {"action": "route", "domain": "topups", "intent": "topup_status", "confidence": 0.84, "reason": "topup_status_signal", "safety": {"requires_human": False, "signals": []}}
    if _has(text, r"\bpending\b") and _has(text, r"\b(?:gas|fuel|petrol|petrol station)\b"):
        return {"action": "route", "domain": "payments", "intent": "pending_card_payment", "confidence": 0.80, "reason": "pending_payment_signal", "safety": {"requires_human": False, "signals": []}}
    if _has(text, r"\b(?:withdrawal|cash|money)\b") and _has(text, r"\b(?:exchange rate|different currency|wrong amount|wrong rate)\b"):
        return {"action": "route", "domain": "cash", "intent": "cash_exchange_rate", "confidence": 0.82, "reason": "cash_exchange_signal", "safety": {"requires_human": False, "signals": []}}
    if _has(text, r"\b(?:transfer|transaction)\b") and _has(text, r"\b(?:completed|sent|recipient|receiver|not received|funds.*available)\b"):
        return {"action": "route", "domain": "transfers", "intent": "transfer_not_received", "confidence": 0.82, "reason": "transfer_delivery_signal", "safety": {"requires_human": False, "signals": []}}

    if _has(text, r"\b(?:password|passcode|login|sign[- ]?in|pin|verification|verif\w*|identity check|proving my identit\w*|ident(?:it|if)\w*|reset code|account access)\b"):
        intent = "identity_access"
        if _has(text, r"\b(?:pin|cash machine)\b"):
            intent = "pin_support"
        elif _has(text, r"\b(?:verify|verification|verif\w*|ident(?:it|if)\w*|source of funds|where.*money come from)\b"):
            intent = "identity_verification"
        elif _has(text, r"\b(?:password|passcode|login|sign[- ]?in|reset|access)\b"):
            intent = "account_access"
        return {"action": "route", "domain": "identity_access", "intent": intent, "confidence": 0.86, "reason": "clear_identity_access_signal", "safety": {"requires_human": False, "signals": []}}

    if _has(text, r"\b(?:top[- ]?ups?|topping up|auto(?:matic)?[- ]?top[- ]?ups?|add money automatically)\b"):
        if _has(text, r"\b(?:limit|max(?:imum)?|unlimited)\b"):
            return {"action": "route", "domain": "topups", "intent": "topup_limits", "confidence": 0.86, "reason": "clear_topup_limit_signal", "safety": {"requires_human": False, "signals": []}}
        return {"action": "route", "domain": "topups", "intent": "topup_support", "confidence": 0.82, "reason": "clear_topup_signal", "safety": {"requires_human": False, "signals": []}}

    if _has(text, r"\b(?:refund|chargeback|money back|return.*payment|payment.*reversed|refund.*missing)\b"):
        return {"action": "route", "domain": "refunds", "intent": "refund_support", "confidence": 0.84, "reason": "clear_refund_signal", "safety": {"requires_human": False, "signals": []}}

    if (_has(text, r"\b(?:card|atm|cash machine)\b") and _has(text, r"\b(?:arrive|arrival|delivery|delivered|when will|where is|locate|waiting|still hasn.t arrived|need my card)\b")) or _has(text, r"\b(?:delivered on|delivery date|delivered by|get my card quickly)\b"):
        return {"action": "route", "domain": "card_lifecycle", "intent": "card_delivery", "confidence": 0.84, "reason": "clear_card_delivery_signal", "safety": {"requires_human": False, "signals": []}}

    if _has(text, r"\b(?:cancel|revert)\b") and _has(text, r"\b(?:transfer|transaction)\b"):
        return {"action": "human_review", "domain": "review", "intent": "cancel_transfer", "confidence": 0.90, "reason": "cancellation_requires_review", "safety": {"requires_human": True, "signals": ["irreversible_action"]}}

    if _has(text, r"\b(?:virtual card|disposable virtual card)\b") and _has(text, r"\b(?:get|obtain|order|how do|how can|use|times)\b"):
        return {"action": "human_review", "domain": "review", "intent": "virtual_card_policy", "confidence": 0.78, "reason": "virtual_card_policy_review", "safety": {"requires_human": True, "signals": ["policy_specific"]}}
    if _has(text, r"\b(?:virtual card|disposable virtual card)\b") and _has(text, r"\b(?:not working|isn.t.*working|won.t work|denied|declined|not accepted)\b"):
        return {"action": "human_review", "domain": "review", "intent": "virtual_card_failure", "confidence": 0.84, "reason": "virtual_card_failure_review", "safety": {"requires_human": True, "signals": ["card_failure"]}}

    if _has(text, r"\b(?:why|require|details|comfortable)\b") and _has(text, r"\b(?:identit\w*|verif\w*)\b"):
        return {"action": "route", "domain": "identity_access", "intent": "why_verify_identity", "confidence": 0.80, "reason": "identity_policy_signal", "safety": {"requires_human": False, "signals": []}}

    if _has(text, r"\b(?:card|contactless)\b") and _has(text, r"\b(?:not working|never worked|won.t work|didn.?t work|can.t seem|unable|app|link|enabled)\b"):
        return {"action": "route", "domain": "card_usage", "intent": "card_usage_support", "confidence": 0.80, "reason": "clear_card_usage_signal", "safety": {"requires_human": False, "signals": []}}

    if _has(text, r"\b(?:cash machine|atm|withdraw\w*|cash withdrawal)\b"):
        return {"action": "route", "domain": "cash", "intent": "cash_withdrawal_support", "confidence": 0.82, "reason": "clear_cash_signal", "safety": {"requires_human": False, "signals": []}}

    if _has(text, r"\b(?:transfer|beneficiary|recipient|bank transfer|salary)\b"):
        return {"action": "route", "domain": "transfers", "intent": "transfer_support", "confidence": 0.82, "reason": "clear_transfer_signal", "safety": {"requires_human": False, "signals": []}}

    if _has(text, r"\b(?:card|payment|charge|fee|exchange rates?|currency|currencies|money worth|value in other countries|abroad|statement|transaction)\b"):
        return {"action": "route", "domain": "payments", "intent": "payment_support", "confidence": 0.80, "reason": "clear_payment_signal", "safety": {"requires_human": False, "signals": []}}

    if _has(text, r"\b(?:country|currency|age|close my account|terminate)\b"):
        return {"action": "route", "domain": "account_policy", "intent": "account_policy_support", "confidence": 0.76, "reason": "clear_account_policy_signal", "safety": {"requires_human": False, "signals": []}}

    return {"action": "human_review", "domain": "review", "intent": "ambiguous_request", "confidence": 0.60, "reason": "no_safe_taxonomy_match", "safety": {"requires_human": True, "signals": ["ambiguous_request"]}}
