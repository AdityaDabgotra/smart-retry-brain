import uuid
from sqlalchemy.orm import Session

from app.decision.engine import decide
from app.models.classification import FailureClassification
from app.models.decision import RetryDecision
from app.models.enums import RetryAction, Strategy, TransactionStatus
from app.models.transaction import Transaction


def make_decision(
    db: Session, txn: Transaction, classification: FailureClassification, strategy: Strategy = Strategy.SMART
) -> RetryDecision:
    result = decide(classification.category)

    decision = RetryDecision(
        id=uuid.uuid4(),
        transaction_id=txn.id,
        action=result["action"],
        strategy=strategy,
        scheduled_for=result["scheduled_for"],
        target_channel=result["target_channel"],
    )
    db.add(decision)

    if result["action"] == RetryAction.NO_RETRY:
        txn.status = TransactionStatus.NEEDS_USER_ACTION
    else:
        txn.status = TransactionStatus.SCHEDULED

    return decision