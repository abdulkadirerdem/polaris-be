from fastapi import FastAPI
from app.core.config import settings
from app.api.v1.forecasts.router import router as forecasts_router
from app.api.v1.auth.router import router as auth_router
from app.api.v1.users.router import router as users_router

app = FastAPI(
    title="Polaris Finance API",
    version="0.1.0",
    description="Financial forecasting and data analysis platform"
)

@app.get("/health")
def health():
    return {"status": "ok"}

# v1 routes
app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(users_router, prefix="/api/v1/users", tags=["users"])
app.include_router(forecasts_router, prefix="/api/v1/forecasts", tags=["forecasts"])
