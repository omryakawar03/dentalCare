from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import model_validator


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[4] / ".env",
        extra="ignore",
    )
    app_env: str = "development"
    database_url: str = "postgresql+asyncpg://municipal:local_only_change_me@localhost:5432/nagar_palika"
    redis_url: str = "redis://localhost:6379/0"
    web_origins: list[str] = ["http://localhost:3000"]
    allowed_hosts: list[str] = ["localhost", "127.0.0.1", "testserver"]
    jwt_issuer: str = "digital-nagar-palika"
    jwt_signing_key: str = "development-only-replace-this-signing-key"
    access_token_minutes: int = 10
    refresh_token_days: int = 14

    @model_validator(mode="after")
    def validate_production_secrets(self):
        if self.app_env == "production" and (
            self.jwt_signing_key == "development-only-replace-this-signing-key"
            or self.jwt_signing_key.startswith("replace-with-")
            or len(self.jwt_signing_key.encode("utf-8")) < 32
        ):
            raise ValueError("Production requires a unique JWT_SIGNING_KEY of at least 32 bytes")
        return self


settings = Settings()
