from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Forecast, ShareMaster

async def get_share_id(session: AsyncSession, symbol: str) -> int | None:
    q = select(ShareMaster.id).where(ShareMaster.symbol == symbol)
    res = await session.execute(q)
    row = res.first()
    return row[0] if row else None

async def upsert_forecast(session: AsyncSession, payload: dict) -> int:
    """
    UPSERT benzersiz anahtar: (share_id, model_id, range_days, target_date)
    """
    stmt = insert(Forecast).values(**payload)
    stmt = stmt.on_conflict_do_update(
        index_elements=["share_id", "model_id", "range_days", "target_date"],
        set_={
            "forecast_date": stmt.excluded.forecast_date,
            "model_name": stmt.excluded.model_name,
            "model_version": stmt.excluded.model_version,
            "used_indicators": stmt.excluded.used_indicators,
            "feature_importance": stmt.excluded.feature_importance,
            "prediction": stmt.excluded.prediction,
            "direction": stmt.excluded.direction,
            "confidence": stmt.excluded.confidence,
            "sl_target": stmt.excluded.sl_target,
            "tp_target": stmt.excluded.tp_target,
            "updated_at": "now()",
        },
    ).returning(Forecast.id)
    res = await session.execute(stmt)
    new_id = res.scalar_one()
    return new_id
