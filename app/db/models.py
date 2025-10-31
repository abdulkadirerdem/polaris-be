from sqlalchemy import (
    Column, Integer, String, Date, Numeric, ForeignKey, JSON, CheckConstraint, Boolean, DateTime
)
from sqlalchemy.dialects.postgresql import ARRAY, BIGINT, UUID
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.db.base import Base
import uuid

class ShareMaster(Base):
    __tablename__ = "shares_master"
    id: Mapped[int] = mapped_column(BIGINT, primary_key=True, autoincrement=True)
    symbol: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)

class ModelRegistry(Base):
    __tablename__ = "model_registry"
    id: Mapped[int] = mapped_column(BIGINT, primary_key=True, autoincrement=True)
    model_name: Mapped[str] = mapped_column(String, nullable=False)
    version: Mapped[str] = mapped_column(String, nullable=False)
    type: Mapped[str] = mapped_column(String, nullable=False)

class Forecast(Base):
    __tablename__ = "forecasts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    share_id: Mapped[int] = mapped_column(
        BIGINT, ForeignKey("shares_master.id", ondelete="CASCADE"), index=True
    )
    model_id: Mapped[int | None] = mapped_column(
        BIGINT, ForeignKey("model_registry.id", ondelete="SET NULL"), nullable=True
    )

    forecast_date: Mapped[Date] = mapped_column(Date, nullable=False)
    target_date: Mapped[Date] = mapped_column(Date, nullable=False)
    range_days: Mapped[int] = mapped_column(Integer, nullable=False)

    model_name: Mapped[str] = mapped_column(String, nullable=False)
    model_version: Mapped[str | None] = mapped_column(String, nullable=True)

    used_indicators = Column(ARRAY(String), server_default="{}")
    feature_importance = Column(JSON, nullable=True)

    prediction = Column(Numeric, nullable=True)
    direction = Column(String, nullable=True)  # up|down|neutral
    confidence = Column(Numeric, nullable=True)
    sl_target = Column(Numeric, nullable=True)
    tp_target = Column(Numeric, nullable=True)

    created_at = mapped_column(String, server_default="now()")
    updated_at = mapped_column(String, server_default="now()")

    __table_args__ = (
        CheckConstraint(
            "(direction in ('up','down','neutral')) OR (direction IS NULL)",
            name="forecast_direction_check",
        ),
    )

class User(Base):
    __tablename__ = "users"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    auth_type: Mapped[str] = mapped_column(String, default="email")  # email, google, apple
    
    # Subscription and status
    subscription: Mapped[str | None] = mapped_column(String, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    email_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Timestamps
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default="now()")
    updated_at: Mapped[DateTime | None] = mapped_column(DateTime, nullable=True)
    last_login_at: Mapped[DateTime | None] = mapped_column(DateTime, nullable=True)
    
    # User data stored as JSON
    profile = Column(JSON, nullable=True, default={})  # first_name, last_name, bio, etc.
    favorites = Column(ARRAY(String), nullable=True, default=[])  # Favorite share symbols
    settings = Column(JSON, nullable=True, default={})  # notifications, theme, etc.
    
    # Additional metadata
    phone: Mapped[str | None] = mapped_column(String, nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(String, nullable=True)
    
    __table_args__ = (
        CheckConstraint(
            "auth_type IN ('email', 'google', 'apple')",
            name="user_auth_type_check"
        ),
    )
