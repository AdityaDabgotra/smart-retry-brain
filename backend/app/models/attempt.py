import uuid
from datetime import datetime, timezone

from sqlalchemy import String, Integer, Numeric, DateTime, ForeignKey, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import AttemptOutcome


class RetryAttempt(Base):
    __tablename__ = "retry_attempts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    transaction_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("transactions.id"), index=True)
    decision_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("retry_decisions.id"), nullable=True
    )

    attempt_number: Mapped[int] = mapped_column(Integer)
    channel_used: Mapped[str] = mapped_column(String(32))
    attempted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    outcome: Mapped[AttemptOutcome] = mapped_column(SAEnum(AttemptOutcome, name="attempt_outcome"))
    resulting_error_code: Mapped[str | None] = mapped_column(String(64), nullable=True)
    amount_recovered: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)

    transaction: Mapped["Transaction"] = relationship(back_populates="attempts")
    decision: Mapped["RetryDecision"] = relationship(back_populates="attempts")