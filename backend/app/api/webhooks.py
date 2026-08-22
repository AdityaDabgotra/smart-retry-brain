import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.transaction import Transaction
from app.models.enums import PaymentMethod, TransactionStatus
from app.schemas.webhooks import PaymentFailedWebhook, TransactionOut

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


@router.post("/payment-failed", response_model=TransactionOut, status_code=201)
def payment_failed(payload: PaymentFailedWebhook, db: Session = Depends(get_db)):
    try:
        method = PaymentMethod(payload.payment_method)
    except ValueError:
        raise HTTPException(400, f"Unknown payment_method: {payload.payment_method}")

    existing = db.query(Transaction).filter_by(external_txn_id=payload.external_txn_id).first()
    if existing:
        raise HTTPException(409, "Transaction already ingested")

    txn = Transaction(
        id=uuid.uuid4(),
        external_txn_id=payload.external_txn_id,
        merchant_id=payload.merchant_id,
        amount=payload.amount,
        currency=payload.currency,
        payment_method=method,
        bank=payload.bank,
        error_code=payload.error_code,
        error_description=payload.error_description,
        status=TransactionStatus.PENDING,
    )
    db.add(txn)
    db.commit()
    db.refresh(txn)

    return TransactionOut(id=str(txn.id), external_txn_id=txn.external_txn_id, status=txn.status.value)