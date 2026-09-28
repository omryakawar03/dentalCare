from functools import lru_cache

from pydantic import SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "DentalCare"
    environment: str = "development"
    api_v1_prefix: str = "/api/v1"
    database_url: str = "postgresql+asyncpg://clinic:clinic@localhost:5432/clinic"
    redis_url: str = "redis://localhost:6379/0"
    jwt_secret: SecretStr = SecretStr("change-me-before-deploying-32-characters")
    jwt_issuer: str = "dentalcare-api"
    access_token_minutes: int = 10
    refresh_token_days: int = 30
    allowed_origins: list[str] = ["http://localhost:3000"]

    @field_validator("jwt_secret")
    @classmethod
    def require_secret_in_production(cls, value: SecretStr, info):
        environment = info.data.get("environment", "development")
        if environment == "production" and len(value.get_secret_value()) < 32:
            raise ValueError("JWT_SECRET must contain at least 32 characters in production")
        if environment == "production" and value.get_secret_value().startswith("change-me"):
            raise ValueError("JWT_SECRET must be configured in production")
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
