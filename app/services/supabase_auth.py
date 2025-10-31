import httpx
import logging
from typing import Optional, Dict, Any
from app.core.config import settings
from app.core.exceptions import (
    SignupError, EmailNotConfirmedError, InvalidCredentialsError, 
    UserNotFoundError, AuthenticationError
)

logger = logging.getLogger(__name__)

class SupabaseAuthService:
    def __init__(self):
        self.supabase_url = settings.SUPABASE_URL
        self.anon_key = settings.SUPABASE_ANON_KEY
        self.headers = {
            "apikey": self.anon_key,
            "Content-Type": "application/json"
        }
    
    async def sign_up(self, email: str, password: str) -> Dict[str, Any]:
        """Register a new user with email and password"""
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                f"{self.supabase_url}/auth/v1/signup",
                headers=self.headers,
                json={
                    "email": email,
                    "password": password,
                    "gotrue_meta_security": {"captcha_token": None}
                }
            )
            
            logger.info(f"Signup response status: {response.status_code}")
            logger.info(f"Signup response content: {response.text}")
            
            if response.status_code not in [200, 201]:
                error_data = response.json() if response.content else {}
                error_msg = error_data.get("msg", "Signup failed")
                error_code = error_data.get("code", "signup_failed")
                logger.error(f"Signup error - Code: {error_code}, Message: {error_msg}")
                raise SignupError(error_msg, error_code)
            
            # Parse successful response
            try:
                result = response.json()
                logger.info(f"Signup successful response: {result}")
                
                # Handle both direct user object and wrapped responses
                if "user" in result:
                    return result
                elif isinstance(result, dict) and "id" in result and "email" in result:
                    # Direct user object
                    return {"user": result}
                else:
                    logger.warning(f"Unexpected signup response format: {result}")
                    return {"user": result}
                    
            except Exception as e:
                logger.error(f"Failed to parse signup response: {e}")
                logger.error(f"Raw response: {response.text}")
                raise SignupError(f"Failed to parse signup response: {e}", "parse_error")
    
    async def sign_in(self, email: str, password: str) -> Dict[str, Any]:
        """Sign in user with email and password"""
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                f"{self.supabase_url}/auth/v1/token?grant_type=password",
                headers=self.headers,
                json={
                    "email": email,
                    "password": password,
                    "gotrue_meta_security": {"captcha_token": None}
                }
            )
            
            if response.status_code != 200:
                error_data = response.json() if response.content else {}
                error_code = error_data.get("code", "unknown")
                error_msg = error_data.get("msg", "Sign in failed")
                
                logger.warning(f"Signin error - Code: {error_code}, Message: {error_msg}")
                
                # Map Supabase error codes to custom exceptions
                error_code_str = str(error_code).lower() if error_code else ""
                error_msg_str = str(error_msg).lower() if error_msg else ""
                
                if "email_not_confirmed" in error_msg_str or "confirmation" in error_msg_str:
                    raise EmailNotConfirmedError(error_msg)
                elif "invalid" in error_msg_str or "invalid" in error_code_str:
                    raise InvalidCredentialsError(error_msg)
                elif "not_found" in error_msg_str or "not found" in error_code_str:
                    raise UserNotFoundError(error_msg)
                else:
                    # Generic authentication error
                    raise AuthenticationError(error_msg, error_code)
            
            return response.json()
    
    async def sign_out(self, access_token: str) -> bool:
        """Sign out user (invalidate token)"""
        headers = {
            **self.headers,
            "Authorization": f"Bearer {access_token}"
        }
        
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                f"{self.supabase_url}/auth/v1/logout",
                headers=headers
            )
            
            return response.status_code == 204
    
    async def reset_password(self, email: str) -> bool:
        """Send password reset email"""
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                f"{self.supabase_url}/auth/v1/recover",
                headers=self.headers,
                json={"email": email}
            )
            
            if response.status_code not in [200, 204]:
                error_data = response.json() if response.content else {}
                raise Exception(error_data.get("msg", "Password reset failed"))
            
            return True
    
    async def verify_email(self, token: str) -> Dict[str, Any]:
        """Verify email with token from reset link"""
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(
                f"{self.supabase_url}/auth/v1/verify",
                headers=self.headers,
                params={"token": token, "type": "signup"}
            )
            
            if response.status_code != 200:
                error_data = response.json() if response.content else {}
                raise Exception(error_data.get("msg", "Email verification failed"))
            
            return response.json()
    
    async def resend_verification_email(self, email: str) -> bool:
        """Resend email verification link"""
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                f"{self.supabase_url}/auth/v1/recover",
                headers=self.headers,
                json={"email": email, "gotrue_meta_security": {"captcha_token": None}}
            )
            
            if response.status_code not in [200, 204]:
                error_data = response.json() if response.content else {}
                raise Exception(error_data.get("msg", "Failed to resend verification email"))
            
            return True
    
    async def get_user(self, access_token: str) -> Dict[str, Any]:
        """Get current user info"""
        headers = {
            **self.headers,
            "Authorization": f"Bearer {access_token}"
        }
        
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(
                f"{self.supabase_url}/auth/v1/user",
                headers=headers
            )
            
            if response.status_code != 200:
                error_data = response.json() if response.content else {}
                raise Exception(error_data.get("msg", "Get user failed"))
            
            return response.json()
    
    async def update_user(self, access_token: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update user metadata"""
        headers = {
            **self.headers,
            "Authorization": f"Bearer {access_token}"
        }
        
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.put(
                f"{self.supabase_url}/auth/v1/user",
                headers=headers,
                json=data
            )
            
            if response.status_code != 200:
                error_data = response.json() if response.content else {}
                raise Exception(error_data.get("msg", "Update user failed"))
            
            return response.json()
    
    async def delete_user(self, access_token: str) -> bool:
        """Delete user account"""
        headers = {
            **self.headers,
            "Authorization": f"Bearer {access_token}"
        }
        
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.delete(
                f"{self.supabase_url}/auth/v1/admin/users",
                headers=headers
            )
            
            return response.status_code == 200

# Create singleton instance
supabase_auth = SupabaseAuthService()