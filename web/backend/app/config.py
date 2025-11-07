"""Application configuration using pydantic settings."""

from __future__ import annotations

from functools import lru_cache
from typing import List

from pydantic import AnyUrl, BaseSettings, Field, field_validator


class Settings(BaseSettings):
    app_name: str = Field("Firebird Web Proxy", env="APP_NAME")
    app_env: str = Field("development", env="APP_ENV")
    app_debug: bool = Field(True, env="APP_DEBUG")
    app_host: str = Field("0.0.0.0", env="APP_HOST")
    app_port: int = Field(8001, env="APP_PORT")

    secret_key: str = Field(..., env="SECRET_KEY")
    access_token_expire_minutes: int = Field(60, env="ACCESS_TOKEN_EXPIRE_MINUTES")

    proxy_api_url: AnyUrl = Field(..., env="PROXY_API_URL")
    proxy_primary_token: str = Field("", env="PROXY_PRIMARY_TOKEN")
    proxy_fallback_token: str = Field("", env="PROXY_FALLBACK_TOKEN")
    proxy_timeout: int = Field(30, env="PROXY_TIMEOUT")

    allowed_origins: List[str] = Field(default_factory=list, env="ALLOWED_ORIGINS")

    @field_validator("allowed_origins", mode="before")
    @classmethod
    def _split_origins(cls, value: str | List[str]) -> List[str]:
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value

    class Config:
        env_file = "env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()

