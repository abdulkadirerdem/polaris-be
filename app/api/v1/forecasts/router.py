from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from datetime import date
from typing import Optional, List

from app.core.security import get_current_user
from app.db.base import get_session
from app.db.models import Forecast, ShareMaster
from app.schemas.forecast import ForecastCreate, BulkForecastCreate, ForecastOut
from .repo import get_share_id, upsert_forecast

router = APIRouter()

@router.post("/upsert", response_model=dict)
async def upsert_endpoint(
    body: ForecastCreate,
    user=Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    share_id = await get_share_id(session, body.symbol)
    if not share_id:
        raise HTTPException(status_code=404, detail=f"symbol not found: {body.symbol}")

    payload = body.model_dump()
    payload.pop("symbol")
    payload["share_id"] = share_id

    new_id = await upsert_forecast(session, payload)
    await session.commit()
    return {"id": new_id}

@router.post("/bulk_upsert", response_model=dict)
async def bulk_upsert_endpoint(
    body: BulkForecastCreate,
    user=Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    ids: List[int] = []
    for item in body.items:
        share_id = await get_share_id(session, item.symbol)
        if not share_id:
            raise HTTPException(status_code=404, detail=f"symbol not found: {item.symbol}")
        payload = item.model_dump()
        payload.pop("symbol")
        payload["share_id"] = share_id
        ids.append(await upsert_forecast(session, payload))
    await session.commit()
    return {"count": len(ids), "ids": ids}

@router.get("/latest", response_model=List[ForecastOut])
async def latest_per_symbol(
    symbol: str = Query(...),
    range_days: Optional[int] = Query(None),
    user=Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    # son forecast_date’e göre en güncel hedefler
    share_id = await get_share_id(session, symbol)
    if not share_id:
        raise HTTPException(status_code=404, detail=f"symbol not found: {symbol}")

    subq = select(func.max(Forecast.forecast_date)).where(Forecast.share_id == share_id)
    if range_days:
        subq = subq.where(Forecast.range_days == range_days)
    subq = subq.scalar_subquery()

    q = select(
        Forecast.id,
        Forecast.share_id,
        Forecast.model_id,
        Forecast.forecast_date,
        Forecast.target_date,
        Forecast.range_days,
        Forecast.model_name,
        Forecast.model_version,
        Forecast.used_indicators,
        Forecast.feature_importance,
        Forecast.prediction,
        Forecast.direction,
        Forecast.confidence,
        Forecast.sl_target,
        Forecast.tp_target,
    ).where(
        and_(
            Forecast.share_id == share_id,
            Forecast.forecast_date == subq
        )
    )
    if range_days:
        q = q.where(Forecast.range_days == range_days)

    res = await session.execute(q)
    rows = [dict(r) for r in res.mappings().all()]
    # enrich with symbol for schema compatibility
    for r in rows:
        r["symbol"] = symbol
    return rows

@router.get("/", response_model=List[ForecastOut])
async def search_forecasts(
    symbol: str,
    range_days: Optional[int] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    user=Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    share_id = await get_share_id(session, symbol)
    if not share_id:
        raise HTTPException(status_code=404, detail=f"symbol not found: {symbol}")

    q = select(Forecast).where(Forecast.share_id == share_id)
    if range_days:
        q = q.where(Forecast.range_days == range_days)
    if date_from:
        q = q.where(Forecast.target_date >= date_from)
    if date_to:
        q = q.where(Forecast.target_date <= date_to)

    res = await session.execute(q)
    items = []
    for f in res.scalars().all():
        d = {
            "id": f.id,
            "symbol": symbol,
            "range_days": f.range_days,
            "forecast_date": f.forecast_date,
            "target_date": f.target_date,
            "model_name": f.model_name,
            "model_version": f.model_version,
            "model_id": f.model_id,
            "used_indicators": f.used_indicators,
            "feature_importance": f.feature_importance,
            "prediction": f.prediction,
            "direction": f.direction,
            "confidence": f.confidence,
            "sl_target": f.sl_target,
            "tp_target": f.tp_target,
        }
        items.append(d)
    return items
