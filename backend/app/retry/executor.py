import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.attempt import RetryAttempt
from app.models.decision import RetryDecision
from app.models.enums import AttemptOutcome, RetryAction, TransactionStatus
from app.models.transaction import Transaction
from app.simulator.bank import simulate_retry

MAX_ATTEMPTS = 3
BACKOFF_BASE_MINUTES = 1
BACKOFF_MULTIPLIER = 2


def execute_due_retries(db: Session) -> int:
    now = datetime.now(timezone.utc)

    due = (
        db.query(RetryDecision)
        .join(Transaction, Transaction.id == RetryDecision.transaction_id)
        .filter(
            RetryDecision.action.in_(
                [RetryAction.RETRY_IMMEDIATE, RetryAction.RETRY_SCHEDULED, RetryAction.SWITCH_CHANNEL]
            ),
            RetryDecision.scheduled_for <= now,
            Transaction.status == TransactionStatus.SCHEDULED,
        )
        .all()
    )

    executed = 0
    for decision in due:
        txn = decision.transaction
        classification = txn.classifications[-1] if txn.classifications else None
        category = classification.category if classification else None

        attempt_number = len(txn.attempts) + 1
        channel = decision.target_channel or txn.payment_method.value
        success = simulate_retry(category) if category else False

        db.add(
            RetryAttempt(
                id=uuid.uuid4(),
                transaction_id=txn.id,
                decision_id=decision.id,
                attempt_number=attempt_number,
                channel_used=channel,
                outcome=AttemptOutcome.SUCCESS if success else AttemptOutcome.FAILURE,
                resulting_error_code=None if success else txn.error_code,
                amount_recovered=txn.amount if success else None,
            )
        )

        if success:
            txn.status = TransactionStatus.RECOVERED
        elif attempt_number >= MAX_ATTEMPTS:
            txn.status = TransactionStatus.FAILED_PERMANENTLY
        else:
            backoff = timedelta(minutes=BACKOFF_BASE_MINUTES * (BACKOFF_MULTIPLIER**attempt_number))
            decision.scheduled_for = now + (backoff / settings.demo_time_scale)
            # status stays SCHEDULED — will be picked up again next poll

        executed += 1

    db.commit()
    return executed