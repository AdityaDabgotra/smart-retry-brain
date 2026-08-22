import uuid
from datetime import datetime, timezone

from sqlalchemy import String, DateTime, ForeignKey, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import RetryAction, Strategy


class RetryDecision(Base):
    __tablename__ = "retry_decisions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    transaction_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("transactions.id"), index=True)

    action: Mapped[RetryAction] = mapped_column(SAEnum(RetryAction, name="retry_action"))
    strategy: Mapped[Strategy] = mapped_column(SAEnum(Strategy, name="strategy"), default=Strategy.SMART)

    scheduled_for: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    target_channel: Mapped[str | None] = mapped_column(String(32), nullable=True)
    explanation: Mapped[str | None] = mapped_column(String(1024), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    transaction: Mapped["Transaction"] = relationship(back_populates="decisions")
    attempts: Mapped[list["RetryAttempt"]] = relationship(back_populates="decision")