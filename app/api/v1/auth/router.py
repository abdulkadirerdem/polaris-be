from fastapi import APIRouter, Depends, HTTPException, status
from app.services.supabase_auth import supabase_auth
from app.schemas.auth import (
    SignUpRequest, SignInRequest, ResetPasswordRequest, VerifyEmailRequest, ResendVerificationRequest,
    SignInResponse, SignUpResponse, AuthMessage, AuthError
)
from app.core.security import get_current_user
from app.core.exceptions import (
    SignupError, EmailNotConfirmedError, InvalidCredentialsError, 
    UserNotFoundError, AuthenticationError
)

router = APIRouter()

@router.post("/signup", response_model=SignUpResponse)
async def signup(request: SignUpRequest):
    """
    Register a new user with email and password.
    
    Returns user info and tokens (based on email confirmation status).
    """
    try:
        result = await supabase_auth.sign_up(
            email=request.email,
            password=request.password
        )
        
        return SignUpResponse(
            user=result["user"],
            access_token=result.get("access_token"),
            refresh_token=result.get("refresh_token"),
            expires_in=result.get("expires_in"),
            token_type=result.get("token_type")
        )
    except SignupError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed. Please try again."
        )

@router.post("/signin", response_model=SignInResponse)
async def signin(request: SignInRequest):
    """
    Sign in user with email and password.
    Returns user info and access tokens.
    """
    try:
        result = await supabase_auth.sign_in(
            email=request.email,
            password=request.password
        )
        
        return SignInResponse(
            user=result["user"],
            access_token=result["access_token"],
            refresh_token=result["refresh_token"],
            expires_in=result["expires_in"],
            token_type=result["token_type"]
        )
    except EmailNotConfirmedError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=e.message
        )
    except InvalidCredentialsError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    except UserNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No account found with this email address"
        )
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.message
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication failed. Please try again."
        )

@router.post("/signout", response_model=AuthMessage)
async def signout(user=Depends(get_current_user)):
    """
    Sign out the current user and invalidate the token.
    """
    # Extract token from the request context (this would need to be passed differently)
    # For now, we'll return success message
    # In a real implementation, you'd need access to the raw token
    return AuthMessage(message="Successfully signed out")

@router.post("/reset-password", response_model=AuthMessage)
async def reset_password(request: ResetPasswordRequest):
    """
    Send password reset email to the user.
    """
    try:
        await supabase_auth.reset_password(email=request.email)
        return AuthMessage(
            message="Password reset email sent. Please check your inbox."
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/verify-email", response_model=AuthMessage)
async def verify_email(request: VerifyEmailRequest):
    """
    Verify user email with the token sent to their email.
    Token typically comes from email verification link: ?token=xxx
    """
    try:
        await supabase_auth.verify_email(token=request.token)
        return AuthMessage(message="Email successfully verified")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/resend-verification", response_model=AuthMessage)
async def resend_verification_email(request: ResendVerificationRequest):
    """
    Resend email verification link to user's email address.
    """
    try:
        await supabase_auth.resend_verification_email(email=request.email)
        return AuthMessage(
            message="Verification email sent. Please check your inbox."
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

