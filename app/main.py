from fastapi import FastAPI
from app.core.config import settings
from app.api.v1.forecasts.router import router as forecasts_router

app = FastAPI(title="Polaris Finance API", version="0.1.0")

@app.get("/health")
def health():
    return {"status": "ok"}

# v1 routes
app.include_router(forecasts_router, prefix="/api/v1/forecasts", tags=["forecasts"])
