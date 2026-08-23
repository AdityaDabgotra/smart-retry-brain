import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import asyncio
from sqlalchemy import select

from app.db.session import SessionLocal
from app.explanation.service import generate_explanation
from app.models.transaction import Transaction # noqa: F401
from app.models.decision import RetryDecision


async def main():
    db = SessionLocal()
    try:
        pending = db.execute(
            select(RetryDecision).where(RetryDecision.explanation.is_(None))
        ).scalars().all()
        print(f"Generating explanations for {len(pending)} decisions...")

        for i, decision in enumerate(pending):
            txn = decision.transaction
            classification = txn.classifications[-1]
            decision.explanation = await generate_explanation(
                txn.error_description, classification.category, decision.action
            )
            if (i + 1) % 25 == 0:
                db.commit()
                print(f"...{i + 1}/{len(pending)}")
        db.commit()
        print("Done.")
    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(main())