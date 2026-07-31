import asyncio
import logging

import pytest
from fastapi import HTTPException
from pydantic import SecretStr
from pytest import LogCaptureFixture

from event_collector.api.routes.argocd import (
    ArgoCDNotificationPayload,
    receive_argocd_notification,
    verify_webhook_token,
)
from event_collector.config import Settings


def test_argocd_notification_is_accepted_with_valid_token(
    caplog: LogCaptureFixture,
) -> None:
    caplog.set_level(logging.INFO, logger="event_collector.api.routes.argocd")
    payload = ArgoCDNotificationPayload(
        application="payments",
        sync_status="Synced",
        health_status="Healthy",
        phase="Succeeded",
        revision="abc123",
        git_commit_hash="abc123",
        deployment_time="2026-07-30T09:45:00Z",
        deployment_started_at="2026-07-30T13:22:18Z",
        deployment_finished_at="2026-07-30T13:22:25Z",
        notification_generated_at="2026-07-30T13:22:26Z",
        sync_duration_seconds=7,
        notification_delay_seconds=1.3262909889999999,
        commit_timestamp="2026-01-28T09:55:44Z",
        commit_age_at_deployment_seconds=15823601,
    )
    settings = Settings(argocd_webhook_token=SecretStr("secret-token"))

    response = asyncio.run(
        receive_argocd_notification(payload, settings, "secret-token")
    )

    assert response.status == "accepted"
    assert response.application == "payments"
    log_record = caplog.records[0]
    assert log_record.message.startswith("argocd notification accepted: ")
    assert '"application":"payments"' in log_record.message
    assert log_record.__dict__["argocd.application"] == "payments"
    assert log_record.__dict__["argocd.sync_status"] == "Synced"
    assert log_record.__dict__["argocd.health_status"] == "Healthy"
    assert log_record.__dict__["argocd.phase"] == "Succeeded"
    assert log_record.__dict__["argocd.revision"] == "abc123"
    assert log_record.__dict__["argocd.git_commit_hash"] == "abc123"
    assert log_record.__dict__["argocd.deployment_time"] == "2026-07-30T09:45:00Z"
    assert log_record.__dict__["argocd.deployment_started_at"] == (
        "2026-07-30T13:22:18Z"
    )
    assert log_record.__dict__["argocd.deployment_finished_at"] == (
        "2026-07-30T13:22:25Z"
    )
    assert log_record.__dict__["argocd.notification_generated_at"] == (
        "2026-07-30T13:22:26Z"
    )
    assert log_record.__dict__["argocd.sync_duration_seconds"] == 7
    assert log_record.__dict__["argocd.notification_delay_seconds"] == (
        1.3262909889999999
    )
    assert log_record.__dict__["argocd.commit_timestamp"] == "2026-01-28T09:55:44Z"
    assert log_record.__dict__["argocd.commit_age_at_deployment_seconds"] == 15823601


def test_argocd_notification_rejects_invalid_token() -> None:
    settings = Settings(argocd_webhook_token=SecretStr("secret-token"))

    with pytest.raises(HTTPException) as exc:
        verify_webhook_token(settings, "wrong-token")

    assert exc.value.status_code == 401


def test_argocd_notification_allows_missing_token_when_unconfigured() -> None:
    verify_webhook_token(Settings(argocd_webhook_token=None), None)


def test_production_requires_argocd_webhook_token() -> None:
    with pytest.raises(ValueError, match="APP_ARGOCD_WEBHOOK_TOKEN"):
        Settings(environment="production", argocd_webhook_token=None)
