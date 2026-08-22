import re
from app.models.enums import FailureCategory

RULE_PATTERNS: list[tuple[re.Pattern, FailureCategory]] = [
    (re.compile(r"insufficient balance", re.I), FailureCategory.INSUFFICIENT_FUNDS),
    (re.compile(r"bank server is currently down|not responding", re.I), FailureCategory.BANK_TIMEOUT),
    (re.compile(r"network issue", re.I), FailureCategory.NETWORK_ERROR),
    (re.compile(r"otp entered is incorrect|otp mismatch", re.I), FailureCategory.OTP_MISMATCH),
    (re.compile(r"card has expired|card expired", re.I), FailureCategory.CARD_EXPIRED),
]


def match_rule(error_description: str) -> FailureCategory | None:
    for pattern, category in RULE_PATTERNS:
        if pattern.search(error_description):
            return category
    return None