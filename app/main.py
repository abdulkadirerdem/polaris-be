from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="FastAPI Starter", version="0.1.0")

class Ping(BaseModel):
    message: str = "pong"

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/ping", response_model=Ping)
def ping():
    return Ping()
