from pydantic import BaseModel,Field

class PaymentFailedWebhook(BaseModel):
    external_txn_id: str = Field(..., description="Gateway's transaction/payment id")
    merchant_id: str
    amount: float
    currency: str = "INR"
    payment_method: str  # upi | card | netbanking | wallet
    bank: str | None = None
    error_code: str
    error_description: str


class TransactionOut(BaseModel):
    id: str
    external_txn_id: str
    status: str

    class Config:
        from_attributes = True