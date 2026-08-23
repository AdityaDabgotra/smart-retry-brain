from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.attempt import RetryAttempt
from app.models.decision import RetryDecision
from app.models.enums import AttemptOutcome, Strategy

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/summary")
def summary(db: Session = Depends(get_db)):
    result = {}
    for strategy in Strategy:
        rows = (
            db.query(RetryAttempt)
            .join(RetryDecision, RetryDecision.id == RetryAttempt.decision_id)
            .filter(RetryDecision.strategy == strategy)
            .all()
        )
        successes = [r for r in rows if r.outcome == AttemptOutcome.SUCCESS]
        result[strategy.value] = {
            "total_attempts": len(rows),
            "successful_recoveries": len(successes),
            "transactions_recovered": len({r.transaction_id for r in successes}),
            "recovered_revenue": round(sum(float(r.amount_recovered) for r in successes), 2),
        }

    smart, naive = result.get("smart", {}), result.get("naive", {})
    result["comparison"] = {
        "revenue_uplift": round(smart.get("recovered_revenue", 0) - naive.get("recovered_revenue", 0), 2),
        "additional_transactions_recovered": smart.get("transactions_recovered", 0) - naive.get("transactions_recovered", 0),
        "wasted_attempts_avoided": naive.get("total_attempts", 0) - smart.get("total_attempts", 0),
    }
    return result