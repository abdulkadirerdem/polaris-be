class AuthenticationError(Exception):
    """Base authentication error"""
    def __init__(self, message: str, code: str = None):
        self.message = message
        self.code = code
        super().__init__(message)

class EmailNotConfirmedError(AuthenticationError):
    """Email not verified error"""
    def __init__(self, message: str = "Please verify your email first. Check your inbox for the verification link."):
        super().__init__(message, "email_not_confirmed")

class InvalidCredentialsError(AuthenticationError):
    """Invalid email or password error"""
    def __init__(self, message: str = "Invalid email or password"):
        super().__init__(message, "invalid_credentials")

class UserNotFoundError(AuthenticationError):
    """User not found error"""
    def __init__(self, message: str = "No account found with this email address"):
        super().__init__(message, "user_not_found")

class SignupError(AuthenticationError):
    """Signup related error"""
    def __init__(self, message: str, code: str = "signup_failed"):
        super().__init__(message, code)