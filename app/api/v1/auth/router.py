from fastapi import APIRouter, Depends
from app.core.security import get_current_user

router = APIRouter()

@router.get("/me")
async def me(user=Depends(get_current_user)):
    return {"user_id": user["user_id"], "role": user.get("role")}

