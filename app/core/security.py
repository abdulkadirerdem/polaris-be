from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from cachetools import TTLCache
import httpx, jwt
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)
security = HTTPBearer(auto_error=True)
_jwks_cache = TTLCache(maxsize=2, ttl=6 * 3600)


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
        # First, decode without verification to see the algorithm
        unverified_header = jwt.get_unverified_header(token.credentials)
        algorithm = unverified_header.get("alg")

        logger.info(f"JWT Algorithm: {algorithm}")

        if algorithm == "HS256":
            # For Supabase HS256 tokens, use JWT secret
            if not settings.SUPABASE_JWT_SECRET:
                logger.warning(
                    "SUPABASE_JWT_SECRET not configured for HS256 tokens - DECODE ONLY FOR TESTING"
                )
                # Decode without verification for testing only
                payload = jwt.decode(
                    token.credentials,
                    options={"verify_signature": False},
                    algorithms=["HS256"],
                    audience=settings.SUPABASE_JWT_AUD,
                )
            else:
                payload = jwt.decode(
                    token.credentials,
                    settings.SUPABASE_JWT_SECRET,
                    algorithms=["HS256"],
                    audience=settings.SUPABASE_JWT_AUD,
                )
        elif algorithm == "RS256":
            # For RS256 tokens, use JWKS
            jwks = await _get_jwks()
            kid = unverified_header["kid"]
            key = next(k for k in jwks["keys"] if k["kid"] == kid)
            public_key = jwt.algorithms.RSAAlgorithm.from_jwk(key)
            payload = jwt.decode(
                token.credentials,
                public_key,
                algorithms=["RS256"],
                audience=settings.SUPABASE_JWT_AUD,
            )
        else:
            logger.error(f"Unsupported JWT algorithm: {algorithm}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Unsupported token algorithm: {algorithm}",
            )

    except jwt.ExpiredSignatureError:
        logger.warning("Token has expired")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired"
        )
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid token: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed"
        )
        
    # Supabase auth uid
    return {
        "user_id": payload.get("sub"),
        "role": payload.get("role"),
        "email": payload.get("email"),
        "email_verified": payload.get("user_metadata", {}).get("email_verified", False),
    }
