from unittest.mock import MagicMock, patch

from fhir_validator_agent.cli import main


@patch("fhir_validator_agent.cli.FhirValidatorService")
def test_cli_valid_query(mock_service_cls, capsys):
    mock_service = MagicMock()
    mock_service.validate_query.return_value = {"valid": True, "errors": []}
    mock_service_cls.from_env.return_value = mock_service

    exit_code = main(["https://example.com/Patient?gender=male"])

    assert exit_code == 0
    captured = capsys.readouterr()
    assert "Valid: True" in captured.out


@patch("fhir_validator_agent.cli.FhirValidatorService")
def test_cli_invalid_query(mock_service_cls, capsys):
    mock_service = MagicMock()
    mock_service.validate_query.return_value = {
        "valid": False,
        "errors": ["Value 'fe' for 'Patient.gender' is not allowed."],
    }
    mock_service_cls.from_env.return_value = mock_service

    exit_code = main(["https://example.com/Patient?gender=fe"])

    assert exit_code == 1
    captured = capsys.readouterr()
    assert "Valid: False" in captured.out
    assert "fe" in captured.out


def test_cli_usage_error(capsys):
    exit_code = main([])

    assert exit_code == 1
    captured = capsys.readouterr()
    assert "Usage: fhir-validate" in captured.out