from sqlalchemy import (
    Column, Integer, String, Date, Numeric, ForeignKey, JSON, CheckConstraint
)
from sqlalchemy.dialects.postgresql import ARRAY, BIGINT
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.db.base import Base

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
