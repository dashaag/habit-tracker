from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # JWT settings
    SECRET_KEY: str  # Loaded from .env
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Database settings
    DB_CONNECTION_STRING: str

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

settings = Settings()
