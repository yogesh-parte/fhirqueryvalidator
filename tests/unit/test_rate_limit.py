import pytest

from fhir_validator_agent.infrastructure.rate_limit import OutboundRateLimiter, reset_outbound_rate_limiter


@pytest.fixture(autouse=True)
def _reset_rate_limiter():
    reset_outbound_rate_limiter()
    yield
    reset_outbound_rate_limiter()


def test_outbound_rate_limiter_allows_requests_within_limit():
    limiter = OutboundRateLimiter(max_requests=2, window_seconds=60)
    limiter.acquire("https://example.com/metadata")
    limiter.acquire("https://example.com/metadata")


def test_outbound_rate_limiter_blocks_excess_requests():
    limiter = OutboundRateLimiter(max_requests=1, window_seconds=60)
    limiter.acquire("https://example.com/metadata")

    with pytest.raises(ValueError, match="rate limit exceeded"):
        limiter.acquire("https://example.com/metadata")


def test_outbound_rate_limiter_tracks_hosts_independently():
    limiter = OutboundRateLimiter(max_requests=1, window_seconds=60)
    limiter.acquire("https://example.com/metadata")
    limiter.acquire("https://other.example/metadata")


def test_outbound_rate_limiter_rejects_invalid_constructor_values():
    with pytest.raises(ValueError, match="max_requests"):
        OutboundRateLimiter(max_requests=0, window_seconds=60)
    with pytest.raises(ValueError, match="window_seconds"):
        OutboundRateLimiter(max_requests=1, window_seconds=0)