import logging

from fhir_validator_agent.infrastructure.security_audit import (
    log_outbound_blocked,
    log_outbound_failure,
    log_outbound_rate_limited,
    log_outbound_success,
)


def test_security_audit_logs_redacted_urls(caplog):
    caplog.set_level(logging.INFO, logger="fhir_validator_agent.security")

    log_outbound_success("https://example.com:443/metadata?token=secret", "metadata")
    log_outbound_blocked("https://example.com/metadata", "blocked host")
    log_outbound_rate_limited("https://example.com/metadata")
    log_outbound_failure("https://example.com/metadata", "metadata", "timeout")

    messages = [record.message for record in caplog.records]
    assert any("outbound_request_success url=https://example.com/metadata" in message for message in messages)
    assert any("outbound_request_blocked url=https://example.com/metadata reason=blocked host" in message for message in messages)
    assert any("outbound_request_rate_limited url=https://example.com/metadata" in message for message in messages)
    assert any("outbound_request_failed url=https://example.com/metadata kind=metadata error=timeout" in message for message in messages)
    assert all("token=secret" not in message for message in messages)