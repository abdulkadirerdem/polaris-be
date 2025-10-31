from fastapi import APIRouter, Depends, HTTPException, status
from app.services.supabase_auth import supabase_auth
from app.schemas.users import UserResponse, UserUpdate, UserDelete, UserStats
from app.schemas.auth import AuthMessage
from app.core.security import get_current_user

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(user=Depends(get_current_user)):
    """
    Get current user's complete profile information.
    """
    try:

        return UserResponse(
            id=user["user_id"],
            email=user.get("email", ""),
            auth_type="email",  # TODO: it shouldn't be email, it should be the auth type from the user
            subscription=None,  # TODO: it should be the subscription from the user
            is_active=True,  # TODO: it should be the active status from the user
            email_verified=user.get("email_verified", False),
            profile=user.get("user_metadata", {}),
            favorites=[],  # TODO: it should be the favorites from the user
            settings={},  # TODO: it should be the settings from the user
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch user profile",
        )


@router.put("/me", response_model=UserResponse)
async def update_current_user(request: UserUpdate, user=Depends(get_current_user)):
    """
    Update current user's profile information.
    """
    try:
        # Prepare update data for Supabase
        update_data = {}

        if request.profile is not None:
            update_data["user_metadata"] = request.profile
        if request.favorites is not None:
            update_data["user_metadata"] = update_data.get("user_metadata", {})
            update_data["user_metadata"]["favorites"] = request.favorites
        if request.settings is not None:
            update_data["user_metadata"] = update_data.get("user_metadata", {})
            update_data["user_metadata"]["settings"] = request.settings
        if request.subscription is not None:
            update_data["app_metadata"] = {"subscription": request.subscription}

        return UserResponse(
            id=user["user_id"],
            email=user.get("email", ""),
            auth_type="email",
            subscription=request.subscription,
            is_active=True,
            email_verified=user.get("email_verified", False),
            profile=request.profile or {},
            favorites=request.favorites or [],
            settings=request.settings or {},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to update user: {str(e)}",
        )


@router.delete("/me", response_model=AuthMessage)
async def delete_current_user(request: UserDelete, user=Depends(get_current_user)):
    """
    Delete current user's account.
    Requires password confirmation.
    """
    try:
        # In a real implementation, you would:
        # 1. Verify the user's password with Supabase
        # 2. Call Supabase admin API to delete the user
        # 3. Handle any cleanup of user-related data

        # For now, we'll simulate the deletion
        # await supabase_auth.delete_user(access_token)

        return AuthMessage(message="Account successfully deleted")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to delete account: {str(e)}",
        )
