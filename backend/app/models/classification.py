import uuid
from datetime import datetime, timezone

from sqlalchemy import String, Float, DateTime, ForeignKey, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import FailureCategory, ClassifiedBy


class FailureClassification(Base):
    __tablename__ = "failure_classifications"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    transaction_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("transactions.id"), index=True)

    category: Mapped[FailureCategory] = mapped_column(SAEnum(FailureCategory, name="failure_category"))
    confidence: Mapped[float] = mapped_column(Float)
    reasoning: Mapped[str] = mapped_column(String(512))
    classified_by: Mapped[ClassifiedBy] = mapped_column(SAEnum(ClassifiedBy, name="classified_by"))

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    transaction: Mapped["Transaction"] = relationship(back_populates="classifications")