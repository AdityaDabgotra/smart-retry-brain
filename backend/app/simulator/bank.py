import random

from app.models.enums import FailureCategory

SUCCESS_RATES: dict[FailureCategory, float] = {
    FailureCategory.NETWORK_ERROR: 0.70,
    FailureCategory.BANK_TIMEOUT: 0.55,
    FailureCategory.INSUFFICIENT_FUNDS: 0.30,
    FailureCategory.CARD_EXPIRED: 0.80,  # after switching to UPI, unrelated failure mode
    FailureCategory.OTP_MISMATCH: 0.0,
    FailureCategory.UNKNOWN: 0.0,
}


def simulate_retry(category: FailureCategory) -> bool:
    return random.random() < SUCCESS_RATES.get(category, 0.4)