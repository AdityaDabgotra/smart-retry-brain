import asyncio
from sqlalchemy import select

from app.classification.engine import classify_transaction
from app.db.session import SessionLocal
from app.models.enums import TransactionStatus
from app.models.transaction import Transaction


async def main():
    db = SessionLocal()
    try:
        pending_ids = [
            row[0]
            for row in db.execute(
                select(Transaction.id).where(Transaction.status == TransactionStatus.PENDING)
            ).all()
        ]
    finally:
        db.close()

    print(f"Classifying {len(pending_ids)} pending transactions...")
    for i, txn_id in enumerate(pending_ids):
        await classify_transaction(txn_id)
        if (i + 1) % 25 == 0:
            print(f"...{i + 1}/{len(pending_ids)}")
    print("Done.")


if __name__ == "__main__":
    asyncio.run(main())