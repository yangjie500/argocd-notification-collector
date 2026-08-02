from pydantic import SecretStr

from event_collector.config import Settings
from event_collector.observability import otlp_headers


def test_otlp_headers_include_authorization_header() -> None:
    settings = Settings(
        observability_otlp_authorization_header=SecretStr("Api-Token test-token"),
    )

    assert otlp_headers(settings) == {"Authorization": "Api-Token test-token"}


def test_otlp_headers_are_omitted_when_authorization_header_is_empty() -> None:
    settings = Settings(observability_otlp_authorization_header=SecretStr(""))

    assert otlp_headers(settings) is None
