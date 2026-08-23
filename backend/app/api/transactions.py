from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, joinedload

from app.db.session import get_db
from app.models.transaction import Transaction

router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.get("")
def list_transactions(limit: int = 50, db: Session = Depends(get_db)):
    txns = (
        db.query(Transaction)
        .options(joinedload(Transaction.classifications), joinedload(Transaction.decisions))
        .order_by(Transaction.created_at.desc())
        .limit(limit)
        .all()
    )
    out = []
    for t in txns:
        classification = t.classifications[-1] if t.classifications else None
        decision = next((d for d in t.decisions if d.strategy.value == "smart"), None)
        out.append(
            {
                "id": str(t.id),
                "external_txn_id": t.external_txn_id,
                "amount": float(t.amount),
                "payment_method": t.payment_method.value,
                "error_description": t.error_description,
                "status": t.status.value,
                "category": classification.category.value if classification else None,
                "action": decision.action.value if decision else None,
                "explanation": decision.explanation if decision else None,
                "created_at": t.created_at.isoformat(),
            }
        )
    return out