import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import uuid
from datetime import timedelta

from app.db.session import SessionLocal
from app.models.attempt import RetryAttempt
from app.models.decision import RetryDecision
from app.models.enums import AttemptOutcome, RetryAction, Strategy
from app.models.transaction import Transaction
from app.simulator.bank import simulate_retry

MAX_ATTEMPTS = 3
HOURLY_DELAY = timedelta(hours=1)


def main():
    db = SessionLocal()
    try:
        transactions = db.query(Transaction).all()
        print(f"Simulating naive baseline for {len(transactions)} transactions...")

        for i, txn in enumerate(transactions):
            classification = txn.classifications[-1] if txn.classifications else None
            category = classification.category if classification else None
            channel = txn.payment_method.value  # naive never switches channel

            decision = RetryDecision(
                id=uuid.uuid4(),
                transaction_id=txn.id,
                action=RetryAction.RETRY_SCHEDULED,
                strategy=Strategy.NAIVE,
                scheduled_for=txn.created_at + HOURLY_DELAY,
                target_channel=None,
            )
            db.add(decision)
            db.flush()

            for attempt_number in range(1, MAX_ATTEMPTS + 1):
                success = simulate_retry(category, channel, channel) if category else False
                db.add(
                    RetryAttempt(
                        id=uuid.uuid4(),
                        transaction_id=txn.id,
                        decision_id=decision.id,
                        attempt_number=attempt_number,
                        channel_used=channel,
                        attempted_at=txn.created_at + HOURLY_DELAY * attempt_number,
                        outcome=AttemptOutcome.SUCCESS if success else AttemptOutcome.FAILURE,
                        resulting_error_code=None if success else txn.error_code,
                        amount_recovered=txn.amount if success else None,
                    )
                )
                if success:
                    break

            if (i + 1) % 100 == 0:
                db.commit()
                print(f"...{i + 1}/{len(transactions)}")

        db.commit()
        print("Done.")
    finally:
        db.close()


if __name__ == "__main__":
    main()