import uuid
from datetime import datetime,timezone

from sqlalchemy import String, Numeric, DateTime, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import PaymentMethod, TransactionStatus

class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    external_txn_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    merchant_id: Mapped[str] = mapped_column(String(64), index=True)

    amount: Mapped[float] = mapped_column(Numeric(12, 2))
    currency: Mapped[str] = mapped_column(String(8), default="INR")
    payment_method: Mapped[PaymentMethod] = mapped_column(SAEnum(PaymentMethod, name="payment_method"))
    bank: Mapped[str | None] = mapped_column(String(64), nullable=True)

    error_code: Mapped[str] = mapped_column(String(64))
    error_description: Mapped[str] = mapped_column(String(512))

    status: Mapped[TransactionStatus] = mapped_column(
        SAEnum(TransactionStatus, name="transaction_status"), default=TransactionStatus.PENDING
    )

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    classifications: Mapped[list["FailureClassification"]] = relationship(back_populates="transaction")
    decisions: Mapped[list["RetryDecision"]] = relationship(back_populates="transaction")
    attempts: Mapped[list["RetryAttempt"]] = relationship(back_populates="transaction")


from app.models.classification import FailureClassification  # noqa: E402
from app.models.decision import RetryDecision  # noqa: E402
from app.models.attempt import RetryAttempt  # noqa: E402