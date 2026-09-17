import uuid
from datetime import datetime, timezone
from typing import List, TYPE_CHECKING
from sqlalchemy import String, Integer, DateTime, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

if TYPE_CHECKING:
    from app.models.click_log import ClickLog


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class URL(Base):
    """
    URL ORM model representing shortened link records.
    """
    __tablename__ = "urls"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    original_url: Mapped[str] = mapped_column(String(2048), nullable=False, index=True)
    short_code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    click_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False
    )

    # Relationship to ClickLog with cascade deletion
    click_logs: Mapped[List["ClickLog"]] = relationship(
        "ClickLog",
        back_populates="url",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    def __repr__(self) -> str:
        return f"<URL id={self.id} short_code='{self.short_code}' original_url='{self.original_url}'>"
