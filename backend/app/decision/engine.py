from datetime import datetime, timedelta, timezone

from app.core.config import settings
from app.models.enums import FailureCategory, RetryAction

DECISION_MAP: dict[FailureCategory, tuple[RetryAction, int | None, str | None]] = {
    FailureCategory.NETWORK_ERROR: (RetryAction.RETRY_IMMEDIATE, 1, None),
    FailureCategory.BANK_TIMEOUT: (RetryAction.RETRY_SCHEDULED, 30, None),
    FailureCategory.INSUFFICIENT_FUNDS: (RetryAction.RETRY_SCHEDULED, 240, None),
    FailureCategory.OTP_MISMATCH: (RetryAction.NO_RETRY, None, None),
    FailureCategory.CARD_EXPIRED: (RetryAction.SWITCH_CHANNEL, 2, "upi"),
    FailureCategory.UNKNOWN: (RetryAction.NO_RETRY, None, None),
}

DOWNTIME_START_HOUR = 2
DOWNTIME_END_HOUR = 4


def _avoid_bank_downtime(scheduled_for: datetime) -> datetime:
    if DOWNTIME_START_HOUR <= scheduled_for.hour < DOWNTIME_END_HOUR:
        return scheduled_for.replace(hour=DOWNTIME_END_HOUR, minute=0, second=0, microsecond=0)
    return scheduled_for


def decide(category: FailureCategory) -> dict:
    action, delay_minutes, target_channel = DECISION_MAP[category]

    scheduled_for = None
    if action in (RetryAction.RETRY_IMMEDIATE, RetryAction.RETRY_SCHEDULED, RetryAction.SWITCH_CHANNEL):
        demo_delay = timedelta(minutes=delay_minutes) / settings.demo_time_scale
        scheduled_for = datetime.now(timezone.utc) + demo_delay
        if action == RetryAction.RETRY_SCHEDULED:
            scheduled_for = _avoid_bank_downtime(scheduled_for)

    return {"action": action, "scheduled_for": scheduled_for, "target_channel": target_channel}