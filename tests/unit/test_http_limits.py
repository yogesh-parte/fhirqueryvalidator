from unittest.mock import MagicMock

import pytest

from fhir_validator_agent.infrastructure.http_limits import read_json_response


def test_read_json_response_returns_dict():
    response = MagicMock()
    response.content = b'{"resourceType": "CapabilityStatement"}'
    response.json.return_value = {"resourceType": "CapabilityStatement"}

    assert read_json_response(response, max_bytes=1024) == {"resourceType": "CapabilityStatement"}


def test_read_json_response_rejects_oversized_body():
    response = MagicMock()
    response.content = b"x" * 2048

    with pytest.raises(ValueError, match="exceeds maximum size"):
        read_json_response(response, max_bytes=1024)


def test_read_json_response_rejects_non_object_json():
    response = MagicMock()
    response.content = b'["not", "an", "object"]'
    response.json.return_value = ["not", "an", "object"]

    with pytest.raises(ValueError, match="JSON object"):
        read_json_response(response, max_bytes=1024)