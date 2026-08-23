import random

from app.models.enums import FailureCategory

BASE_SUCCESS_RATES: dict[FailureCategory, float] = {
    FailureCategory.NETWORK_ERROR: 0.70,
    FailureCategory.BANK_TIMEOUT: 0.55,
    FailureCategory.INSUFFICIENT_FUNDS: 0.30,
    FailureCategory.OTP_MISMATCH: 0.02,  # blind retry essentially never fixes a wrong OTP
    FailureCategory.UNKNOWN: 0.05,       # genuinely unclear failure, low baseline odds
}

CARD_EXPIRED_SAME_CHANNEL_RATE = 0.02       # retrying the same expired card basically never works
CARD_EXPIRED_SWITCHED_CHANNEL_RATE = 0.80   # switching to UPI usually works


def simulate_retry(category: FailureCategory, channel: str, original_channel: str) -> bool:
    if category == FailureCategory.CARD_EXPIRED:
        rate = CARD_EXPIRED_SWITCHED_CHANNEL_RATE if channel != original_channel else CARD_EXPIRED_SAME_CHANNEL_RATE
        return random.random() < rate
    return random.random() < BASE_SUCCESS_RATES.get(category, 0.4)