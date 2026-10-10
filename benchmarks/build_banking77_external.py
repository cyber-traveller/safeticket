"""Create one-per-intent BANKING77 external evaluation cases.

The source labels stay in each row. Coarse SafeTicket teams are an explicit benchmark
mapping, not labels supplied by BANKING77.
"""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "work" / "external" / "banking77" / "test.csv"
OUT = ROOT / "benchmarks" / "banking77_external_v1.json"

BILLING = {
    "cash_withdrawal_charge", "card_payment_fee_charged", "extra_charge_on_statement",
    "exchange_charge", "exchange_rate", "card_payment_wrong_exchange_rate",
    "wrong_exchange_rate_for_cash_withdrawal", "transaction_charged_twice",
    "pending_card_payment", "reverted_card_payment?", "declined_card_payment",
    "pending_cash_withdrawal", "wrong_amount_of_cash_received", "cash_withdrawal_not_recognised",
    "cash_withdrawal_charge", "pending_top_up", "top_up_by_card_charge",
    "top_up_by_bank_transfer_charge", "top_up_by_cash_or_cheque", "top_up_failed",
    "top_up_limits", "top_up_reverted", "topping_up_by_card", "automatic_top_up",
    "declined_transfer", "failed_transfer", "pending_transfer", "transfer_fee_charged",
    "transfer_into_account", "transfer_timing", "transfer_not_received_by_recipient",
    "balance_not_updated_after_bank_transfer", "balance_not_updated_after_cheque_or_cash_deposit",
    "beneficiary_not_allowed", "receiving_money", "supported_cards_and_currencies",
    "fiat_currency_support", "card_acceptance", "declined_cash_withdrawal",
}
SHIPPING = {"card_arrival", "card_delivery_estimate"}
RETURNS = {"Refund_not_showing_up", "request_refund"}
ACCESS = {
    "passcode_forgotten", "pin_blocked", "change_pin", "verify_my_identity",
    "unable_to_verify_identity", "why_verify_identity", "verify_source_of_funds",
    "verify_top_up", "card_linking", "card_not_working", "contactless_not_working",
    "cash_withdrawal_not_recognised",
}
REVIEW = {
    "activate_my_card", "age_limit", "apple_pay_or_google_pay", "atm_support",
    "automatic_top_up", "card_about_to_expire", "card_swallowed", "compromised_card",
    "country_support", "direct_debit_payment_not_recognised", "disposable_card_limits",
    "edit_personal_details", "exchange_via_app", "get_disposable_virtual_card",
    "get_physical_card", "getting_spare_card", "getting_virtual_card", "lost_or_stolen_card",
    "lost_or_stolen_phone", "order_physical_card", "terminate_account", "visa_or_mastercard",
    "virtual_card_not_working", "card_payment_not_recognised",
}


def team(category):
    if category in SHIPPING:
        return "shipping"
    if category in RETURNS:
        return "returns"
    if category in ACCESS:
        return "access"
    if category in BILLING:
        return "billing"
    return "review"


def main():
    by_category = {}
    with SOURCE.open(newline="") as handle:
        for row in csv.DictReader(handle):
            by_category.setdefault(row["category"], row["text"])
    rows = [
        {"id": f"banking77-{category}", "ticket": text, "source_category": category, "team": team(category)}
        for category, text in sorted(by_category.items())
    ]
    OUT.write_text(json.dumps(rows, indent=2) + "\n")
    print(json.dumps({"cases": len(rows), "teams": {name: sum(r["team"] == name for r in rows) for name in ("billing", "shipping", "returns", "access", "review")}, "path": str(OUT)}, indent=2))


if __name__ == "__main__":
    main()
