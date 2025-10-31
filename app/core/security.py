from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from cachetools import TTLCache
import httpx, jwt

from app.core.config import settings

security = HTTPBearer(auto_error=True)
_jwks_cache = TTLCache(maxsize=2, ttl=6*3600)

async def _get_jwks():
    if "jwks" in _jwks_cache:
        return _jwks_cache["jwks"]
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(settings.SUPABASE_JWKS_URL)
        r.raise_for_status()
        data = r.json()
        _jwks_cache["jwks"] = data
        return data

async def get_current_user(token=Depends(security)):
    try:
        jwks = await _get_jwks()
        unverified = jwt.get_unverified_header(token.credentials)
        kid = unverified["kid"]
        key = next(k for k in jwks["keys"] if k["kid"] == kid)
        public_key = jwt.algorithms.RSAAlgorithm.from_jwk(key)
        payload = jwt.decode(
            token.credentials,
            public_key,
            algorithms=["RS256"],
            audience=settings.SUPABASE_JWT_AUD,
        )
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    # Supabase auth uid
    return {"user_id": payload.get("sub"), "role": payload.get("role")}
