from functools import lru_cache
from typing import Literal, Self

from pydantic import Field, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from event_collector import __version__


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="APP_",
        case_sensitive=False,
        extra="ignore",
    )

    name: str = "event-collector"
    version: str = __version__
    environment: Literal["local", "test", "staging", "production"] = "local"
    log_level: str = "INFO"
    observability_enabled: bool = False
    observability_service_name: str = "event-collector"
    observability_otlp_logs_endpoint: str | None = None
    observability_otlp_authorization_header: SecretStr | None = None
    observability_verify_tls: bool = True

    api_prefix: str = "/api/v1"
    docs_enabled: bool = True

    external_api_url: str = "https://example.invalid"
    external_api_timeout_seconds: float = Field(default=10.0, gt=0)

    argocd_webhook_token: SecretStr | None = None

    @model_validator(mode="after")
    def validate_production_settings(self) -> Self:
        if self.environment == "production" and self.argocd_webhook_token is None:
            msg = "APP_ARGOCD_WEBHOOK_TOKEN must be configured in production"
            raise ValueError(msg)
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
