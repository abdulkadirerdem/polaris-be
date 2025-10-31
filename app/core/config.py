from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_ENV: str = "dev"
    LOG_LEVEL: str = "INFO"
    SUPABASE_URL: str
    SUPABASE_ANON_KEY: str
    SUPABASE_JWKS_URL: str
    SUPABASE_JWT_AUD: str = "authenticated"
    DATABASE_URL: str

    model_config = {"env_file": ".env", "extra": "ignore"}

settings = Settings()
