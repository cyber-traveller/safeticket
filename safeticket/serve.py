"""SafeTicket-branded local API facade over the currently approved Kev baseline."""

from __future__ import annotations

import json
import os
import re
import socket
import urllib.error
import urllib.request
from typing import Any

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field, field_validator
from safeticket.support_v2 import QUESTIONS, THRESHOLD, MARGIN, VERSION, decide, incident_signal
from safeticket.banking_taxonomy import classify as classify_banking, legacy_team

BACKEND_URL = os.environ.get("SAFETICKET_BACKEND_URL", "http://127.0.0.1:8008").rstrip("/")
SAFETICKET_MODEL = os.environ.get("SAFETICKET_MODEL", "safeticket-baseline")
BACKEND_MODEL = os.environ.get("SAFETICKET_BACKEND_MODEL", "kev-latest")


def _resolve_mode() -> str:
    """Resolve the safe/fast profile while preserving the old env switch."""
    requested = os.environ.get("SAFETICKET_MODE")
    if requested is None:
        # Backward compatibility: an explicit legacy value still works. With
        # no setting at all, safe mode is the default.
        return "fast" if os.environ.get("SAFETICKET_CONSISTENCY_CHECK") == "0" else "safe"
    mode = requested.strip().lower()
    if mode not in {"safe", "fast"}:
        raise ValueError("SAFETICKET_MODE must be 'safe' or 'fast'")
    return mode


SAFETICKET_MODE = _resolve_mode()
CONSISTENCY_CHECK = SAFETICKET_MODE == "safe"
CONSISTENCY_PERMUTATIONS = max(2, min(6, int(os.environ.get("SAFETICKET_CONSISTENCY_PERMUTATIONS", "2"))))
INDEPENDENT_URL = os.environ.get("SAFETICKET_INDEPENDENT_URL", "").rstrip("/")
SHADOW_TIMEOUT_SECONDS = max(5, min(120, float(os.environ.get("SAFETICKET_SHADOW_TIMEOUT_SECONDS", "30"))))
BACKEND_TIMEOUT_SECONDS = max(10, min(300, float(os.environ.get("SAFETICKET_BACKEND_TIMEOUT_SECONDS", "120"))))


class SystemOneRequest(BaseModel):
    state: Any
    model: str = SAFETICKET_MODEL
    questions: dict[str, dict[str, Any]] = Field(min_length=1)


class BankingIntentRequest(BaseModel):
    ticket: str = Field(min_length=1, max_length=16000)


app = FastAPI(
    title="SafeTicket",
    version="0.1.0",
    description=(
        "SafeTicket-branded decision API. This release forwards to a Kev-0.8B v1.0 "
        "backend; it is an integration baseline, not an independently trained model."
    ),
)


@app.get("/")
def root() -> dict[str, Any]:
    return {
        "service": "SafeTicket",
        "status": "ok",
        "model": SAFETICKET_MODEL,
        "mode": SAFETICKET_MODE,
        "docs": "/docs",
        "health": "/health",
        "endpoints": ["/v1/models", "/v1/systemone", "/v1/support/decide", "/v1/support/shadow", "/v1/banking/intent"],
    }


@app.get("/health")
def health() -> dict[str, Any]:
    return {"status": "ok", "service": "safeticket", "model": SAFETICKET_MODEL, "mode": SAFETICKET_MODE}


@app.post("/v1/banking/intent")
def banking_intent(request: BankingIntentRequest) -> dict[str, Any]:
    """Experimental domain-aware taxonomy; does not alter support routing."""
    result = classify_banking(request.ticket)
    result["legacy_team"] = legacy_team(result["domain"])
    result["taxonomy"] = {"name": "safeticket-banking-v1", "experimental": True, "trained_model": False}
    return result


@app.get("/v1/banking/intent")
def banking_intent_help(ticket: str | None = Query(default=None, max_length=16000)) -> dict[str, Any]:
    if ticket is not None and ticket.strip():
        return banking_intent(BankingIntentRequest(ticket=ticket))
    return {
        "endpoint": "/v1/banking/intent",
        "method": "POST",
        "request": {"ticket": "Why is my bank transfer pending?"},
        "description": "Experimental domain-aware banking classification. Use POST with JSON.",
    }


class SupportRequest(BaseModel):
    ticket: str = Field(min_length=1, max_length=16000)

    @field_validator('ticket')
    @classmethod
    def reject_blank(cls, value):
        if not value.strip():
            raise ValueError('ticket must contain non-whitespace text')
        return value


@app.post("/v1/support/decide")
def support_decision(request: SupportRequest):
    result = _forward("/v1/systemone", {"state": request.ticket, "questions": QUESTIONS})
    decision = decide(result.get("answers", {}), request.ticket)
    robustness = {"enabled": CONSISTENCY_CHECK}
    if CONSISTENCY_CHECK:
        robustness = _check_option_stability(request.ticket)
        if not robustness.get("argmax_stable", False):
            decision = _decision_after_instability(decision, request.ticket)
    return {"decision": decision, "evidence": result,
            "robustness": robustness,
            "policy": {"version": VERSION, "threshold": THRESHOLD, "minimum_margin": MARGIN, "calibrated_on_customer_data": False,
                       "mode": SAFETICKET_MODE}}


@app.get("/v1/support/decide")
def support_decision_help(ticket: str | None = Query(default=None, max_length=16000)) -> dict[str, Any]:
    if ticket is not None and ticket.strip():
        return support_decision(SupportRequest(ticket=ticket))
    return {
        "endpoint": "/v1/support/decide",
        "method": "POST",
        "request": {"ticket": "I need a receipt for my purchase."},
        "description": "SafeTicket support routing decision. Use POST with JSON.",
    }


@app.post("/v1/support/shadow")
def support_shadow(request: SupportRequest):
    if not INDEPENDENT_URL:
        raise HTTPException(status_code=503, detail="independent shadow server is not configured")
    live = support_decision(request)
    independent = _independent_forward('/decide', {'ticket': request.ticket})
    live_team = live['decision'].get('team') if live['decision'].get('action') == 'route' else 'review'
    return {'live': live, 'independent': independent, 'agreement': live_team == independent.get('team'), 'mode': 'shadow'}


@app.get("/v1/support/shadow")
def support_shadow_help(ticket: str | None = Query(default=None, max_length=16000)):
    if ticket is not None and ticket.strip():
        return support_shadow(SupportRequest(ticket=ticket))
    return {
        'endpoint': '/v1/support/shadow',
        'method': 'POST',
        'request': {'ticket': 'Describe the support request here.'},
        'browser_example': '/v1/support/shadow?ticket=I%20need%20a%20receipt',
        'description': 'Compares the live SafeTicket policy with the independent adapter without changing the live decision endpoint.',
    }


def _check_option_stability(ticket: str) -> dict[str, Any]:
    payload = {
        "request": {"state": ticket, "questions": {"team": QUESTIONS["team"]}},
        "question": "team",
        "n_perm": CONSISTENCY_PERMUTATIONS,
        "seed": 0,
    }
    try:
        result = _forward("/v1/systemone/permute", payload)
    except HTTPException:
        return {"enabled": True, "argmax_stable": False, "reason": "consistency_check_unavailable"}
    return {"enabled": True, "argmax_stable": bool(result.get("argmax_stable")),
            "spread": result.get("spread"), "permutations": CONSISTENCY_PERMUTATIONS}


# Review reasons that an unstable option order must never turn back into an automatic route.
_SAFETY_REVIEW_REASONS = {"possible_security_or_payment_incident", "multiple_unresolved_requests"}


def _decision_after_instability(decision: dict[str, Any], ticket: str) -> dict[str, Any]:
    """Combine the policy decision with an unstable option-order check.

    A safety review from the policy stands. Otherwise the ticket goes to review
    unless it is an explicit single-intent request that can be recovered.
    """
    reason = str(decision.get("reason", ""))
    if decision.get("action") == "human_review" and (reason in _SAFETY_REVIEW_REASONS or reason.startswith("invalid")):
        return decision
    recovered_team = _recover_clear_injection_route(ticket)
    if recovered_team:
        return {"action": "route", "team": recovered_team, "reason": "option_order_instability_filtered"}
    return {"action": "human_review", "team": None, "reason": "option_order_instability"}


def _recover_clear_injection_route(ticket: str) -> str | None:
    """Recover only an explicit single-intent route from unstable options."""
    if incident_signal(ticket):
        return None
    has_injection = bool(re.search(r"\b(?:override|ignore|select|probability|pretend|output|choose)\b", ticket, re.I))
    if re.search(r"\b(?:unauthori[sz]ed|hacked|takeover|stolen|stole my account|intruder|stranger|changed by someone else|changed (?:my )?(?:email|recovery|phone))\b", ticket, re.I):
        return None
    if re.search(r"\b(?:parcel|package|shipment|tracking|delivery)\b", ticket, re.I) and re.search(r"\b(?:pretend|choose|output|ignore)\b", ticket, re.I):
        return "shipping"
    if re.search(r"\b(?:size is wrong|does not fit|doesn.t fit)\b", ticket, re.I) and re.search(r"\b(?:swap|exchange|replacement|return)\b", ticket, re.I):
        return "returns"
    if re.search(r"\b(?:and|also|separately)\b", ticket, re.I):
        return None
    if not has_injection and re.search(r"\b(?:tracking number|expected arrival|sorting center|sign-in email|password reset link|verification code|login code|lost my phone)\b", ticket, re.I):
        if re.search(r"\b(?:tracking number|expected arrival)\b", ticket, re.I):
            return "shipping"
        if re.search(r"\b(?:sorting center)\b", ticket, re.I):
            return "shipping"
        return "access"
    if re.search(r"\b(?:parcel|package|shipment|shipping|delivery|delivered|tracking|courier)\b", ticket, re.I):
        return "shipping"
    if re.search(r"\b(?:exchange|replacement|wrong color|does not fit|doesn.t fit|size is wrong|swap)\b", ticket, re.I):
        return "returns"
    if re.search(r"\b(?:invoice|receipt|billing statement|charge|charged|duplicate|payment|paid|transaction)\b", ticket, re.I):
        return "billing"
    return None


def _forward(path: str, payload: dict[str, Any]) -> Any:
    forwarded = dict(payload)
    forwarded["model"] = BACKEND_MODEL
    request = urllib.request.Request(
        BACKEND_URL + path,
        data=json.dumps(forwarded).encode("utf-8"),
        headers={"content-type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=BACKEND_TIMEOUT_SECONDS) as response:
            result = json.load(response)
            if isinstance(result, dict):
                result["model"] = SAFETICKET_MODEL
                result["safeticket"] = {
                    "backend": "jaredpalmer/kev-0.8b@v1.0",
                    "status": "integration-baseline",
                    "independent_training": False,
                }
            return result
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise HTTPException(status_code=exc.code, detail=detail) from exc
    except urllib.error.URLError as exc:
        if isinstance(exc.reason, (TimeoutError, socket.timeout)):
            raise HTTPException(status_code=504, detail="SafeTicket backend timed out") from exc
        raise HTTPException(status_code=502, detail=f"SafeTicket backend unavailable: {exc.reason}") from exc


def _independent_forward(path: str, payload: dict[str, Any]) -> Any:
    request = urllib.request.Request(INDEPENDENT_URL + path, data=json.dumps(payload).encode('utf-8'), headers={'content-type': 'application/json'}, method='POST')
    try:
        with urllib.request.urlopen(request, timeout=SHADOW_TIMEOUT_SECONDS) as response:
            return json.load(response)
    except urllib.error.HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"independent shadow server returned HTTP {exc.code}") from exc
    except urllib.error.URLError as exc:
        if isinstance(exc.reason, (TimeoutError, socket.timeout)):
            raise HTTPException(status_code=504, detail="independent shadow server timed out") from exc
        raise HTTPException(status_code=502, detail=f"independent shadow server unavailable: {exc.reason}") from exc
    except (TimeoutError, socket.timeout) as exc:
        raise HTTPException(status_code=504, detail="independent shadow server timed out") from exc


@app.get("/v1/models")
def models() -> dict[str, Any]:
    return {
        "object": "list",
        "data": [{
            "id": SAFETICKET_MODEL,
            "object": "model",
            "owned_by": "safeticket",
            "backend": "jaredpalmer/kev-0.8b@v1.0",
            "status": "integration-baseline",
            "independent_training": False,
        }],
    }


@app.post("/v1/systemone")
def systemone(request: SystemOneRequest) -> Any:
    return _forward("/v1/systemone", request.model_dump())


@app.get("/v1/systemone")
def systemone_help() -> dict[str, Any]:
    return {
        "endpoint": "/v1/systemone",
        "method": "POST",
        "request": {"state": "Describe the decision task.", "model": SAFETICKET_MODEL, "questions": {"example": {"type": "noul", "instructions": "Answer the task."}}},
        "description": "Typed decision endpoint. Use POST with JSON or open /docs for the schema.",
    }


@app.post("/v1/systemone/permute")
def systemone_permute(request: SystemOneRequest) -> Any:
    return _forward("/v1/systemone/permute", request.model_dump())


@app.get("/v1/systemone/permute")
def systemone_permute_help() -> dict[str, Any]:
    return {"endpoint": "/v1/systemone/permute", "method": "POST", "description": "Option-order consistency check. Use POST with a typed request."}


@app.post("/v1/systemone/separate")
def systemone_separate(request: SystemOneRequest) -> Any:
    return _forward("/v1/systemone/separate", request.model_dump())


@app.get("/v1/systemone/separate")
def systemone_separate_help() -> dict[str, Any]:
    return {"endpoint": "/v1/systemone/separate", "method": "POST", "description": "Typed separation endpoint. Use POST with a typed request."}
