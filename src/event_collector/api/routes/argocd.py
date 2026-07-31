import logging
from hmac import compare_digest
from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field

from event_collector.config import Settings, get_settings

router = APIRouter(
    prefix="/argocd",
    tags=["argocd"],
)
logger = logging.getLogger(__name__)


class ArgoCDNotificationPayload(BaseModel):
    model_config = ConfigDict(extra="allow")

    application: str = Field(min_length=1)
    project: str | None = None
    sync_status: str | None = None
    health_status: str | None = None
    phase: str | None = None
    revision: str | None = None
    git_commit_hash: str | None = None
    deployment_time: str | None = None
    deployment_started_at: str | None = None
    deployment_finished_at: str | None = None
    notification_generated_at: str | None = None
    sync_duration_seconds: float | None = None
    notification_delay_seconds: float | None = None
    commit_timestamp: str | None = None
    commit_age_at_deployment_seconds: float | None = None
    message: str | None = None


class WebhookAccepted(BaseModel):
    status: str
    application: str


def verify_webhook_token(
    settings: Settings,
    provided_token: str | None,
) -> None:
    expected_token = settings.argocd_webhook_token
    if expected_token is None:
        return

    expected_value = expected_token.get_secret_value()
    if provided_token is None or not compare_digest(provided_token, expected_value):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Argo CD webhook token",
        )


@router.post(
    "/notifications",
    status_code=status.HTTP_202_ACCEPTED,
)
async def receive_argocd_notification(
    payload: ArgoCDNotificationPayload,
    settings: Annotated[Settings, Depends(get_settings)],
    x_event_collector_token: Annotated[
        str | None,
        Header(alias="X-Event-Collector-Token"),
    ] = None,
) -> WebhookAccepted:
    verify_webhook_token(settings, x_event_collector_token)
    payload_data = payload.model_dump(exclude_none=True)
    logger.info(
        "argocd notification accepted: %s",
        payload.model_dump_json(exclude_none=True),
        extra={f"argocd.{key}": value for key, value in payload_data.items()},
    )

    return WebhookAccepted(
        status="accepted",
        application=payload.application,
    )
