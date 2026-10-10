"""Small safety guard used after the independent model's raw label.

This is intentionally deterministic and narrow: it handles instruction text
as untrusted data and escalates account-compromise signals before allowing a
model route. It is a guardrail, not evidence that the base model learned these
rules.
"""
import re


INJECTION = re.compile(r"\b(?:override|ignore|select|probability|pretend|output)\b", re.I)
SECURITY = re.compile(
    r"\b(?:unauthori[sz]ed|hacked|takeover|stolen|intruder|stranger|unknown person|"
    r"changed (?:my )?(?:email|recovery|phone)|accessed my account)\b",
    re.I,
)
BILLING = re.compile(r"\b(?:invoice|receipt|billing statement|charge|charged|duplicate|payment|paid|transaction)\b", re.I)
SHIPPING = re.compile(r"\b(?:parcel|package|shipment|shipping|delivery|delivered|tracking|courier)\b", re.I)
ACCESS = re.compile(r"\b(?:password|sign[- ]?in|login|verification code|reset link|account access|two-factor)\b", re.I)
ACTION = re.compile(r"\b(?:fix|correct|track|locate|return|refund|exchange|cancel|change|reset|unlock|arrange|send|issue)\b", re.I)


def guard_team(ticket: str, model_team: str) -> tuple[str, str]:
    """Return a guarded team and a short reason."""
    text = ticket if isinstance(ticket, str) else ""
    resolved_payment_concern = bool(re.search(
        r"\b(?:not fraud|not unauthorized|legitimate|confirmed .* (?:made|authorized)|made the purchase)\b",
        text,
        re.I,
    ))
    ordinary_password = bool(re.search(
        r"(?:\b(password|sign[- ]?in|login)\b.*\b(locked|wrong|forgot|reset|unlock)\b|"
        r"\b(locked|wrong|forgot|reset|unlock)\b.*\b(password|sign[- ]?in|login)\b)",
        text,
        re.I,
    )) and not SECURITY.search(text)
    if SECURITY.search(text) and not ordinary_password and not resolved_payment_concern:
        return "review", "independent_security_guard"
    if re.search(r"\b(?:and|also|separately)\b", text, re.I) and len(ACTION.findall(text)) >= 2:
        return "review", "independent_multiple_request_guard"
    if INJECTION.search(text):
        if BILLING.search(text):
            return "billing", "independent_injection_filtered_billing"
        if ACCESS.search(text):
            return "access", "independent_injection_filtered_access"
        if SHIPPING.search(text):
            return "shipping", "independent_injection_filtered_shipping"
    return model_team, "independent_model"
