import logging
from dataclasses import dataclass

from opentelemetry._logs import set_logger_provider
from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.resources import Resource

from event_collector.config import Settings

_LOGGER_NAME = "event_collector"
_CONSOLE_HANDLER_MARKER = "event_collector_console_handler"
_HANDLER_MARKER = "event_collector_otel_handler"


@dataclass
class ObservabilityProviders:
    log_provider: LoggerProvider | None = None
    log_handler: logging.Handler | None = None

    def shutdown(self) -> None:
        global _observability_providers

        app_logger = logging.getLogger(_LOGGER_NAME)
        if self.log_handler is not None and self.log_handler in app_logger.handlers:
            app_logger.removeHandler(self.log_handler)
            self.log_handler.close()

        if self.log_provider is not None:
            self.log_provider.shutdown()

        if _observability_providers is self:
            _observability_providers = None


_observability_providers: ObservabilityProviders | None = None


def configure_logging(settings: Settings) -> None:
    app_logger = logging.getLogger(_LOGGER_NAME)
    app_logger.setLevel(_log_level(settings.log_level))

    if not _has_marked_handler(app_logger, _CONSOLE_HANDLER_MARKER):
        console_handler = logging.StreamHandler()
        console_handler.setLevel(_log_level(settings.log_level))
        console_handler.setFormatter(
            logging.Formatter(
                "%(asctime)s %(levelname)s [%(name)s] %(message)s"
            )
        )
        setattr(console_handler, _CONSOLE_HANDLER_MARKER, True)
        app_logger.addHandler(console_handler)


def configure_observability(settings: Settings) -> ObservabilityProviders:
    global _observability_providers

    if not settings.observability_enabled:
        return ObservabilityProviders()

    if _observability_providers is not None:
        return _observability_providers

    resource = Resource.create(
        {
            "service.name": settings.observability_service_name,
            "service.version": settings.version,
            "deployment.environment": settings.environment,
        }
    )

    log_exporter = OTLPLogExporter(endpoint=settings.observability_otlp_logs_endpoint)
    if not settings.observability_verify_tls:
        log_exporter._certificate_file = False  # type: ignore # noqa: SLF001

    log_provider = LoggerProvider(resource=resource)
    log_provider.add_log_record_processor(
        BatchLogRecordProcessor(log_exporter)
    )
    set_logger_provider(log_provider)

    app_logger = logging.getLogger(_LOGGER_NAME)
    otel_handler = _get_marked_handler(app_logger, _HANDLER_MARKER)
    if otel_handler is None:
        otel_handler = LoggingHandler(
            level=_log_level(settings.log_level),
            logger_provider=log_provider,
        )
        setattr(otel_handler, _HANDLER_MARKER, True)
        app_logger.addHandler(otel_handler)

    _observability_providers = ObservabilityProviders(
        log_provider=log_provider,
        log_handler=otel_handler,
    )
    return _observability_providers


def _has_marked_handler(logger: logging.Logger, marker: str) -> bool:
    return _get_marked_handler(logger, marker) is not None


def _get_marked_handler(
    logger: logging.Logger,
    marker: str,
) -> logging.Handler | None:
    for handler in logger.handlers:
        if getattr(handler, marker, False):
            return handler
    return None


def _log_level(level_name: str) -> int:
    level = getattr(logging, level_name.upper(), logging.INFO)
    if isinstance(level, int):
        return level
    return logging.INFO
