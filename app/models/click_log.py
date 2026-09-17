import uuid
from datetime import datetime, timezone
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, DateTime, ForeignKey, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

if TYPE_CHECKING:
    from app.models.url import URL


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class ClickLog(Base):
    """
    ClickLog ORM model tracking individual click events for advanced analytics.
    """
    __tablename__ = "click_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    url_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("urls.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
        index=True
    )
    user_agent: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)

    # Relationship back to URL
    url: Mapped["URL"] = relationship("URL", back_populates="click_logs")

    def __repr__(self) -> str:
        return f"<ClickLog id={self.id} url_id={self.url_id} timestamp={self.timestamp}>"
