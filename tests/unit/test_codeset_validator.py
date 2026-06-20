from fhir_validator_agent.core.codeset_validator import is_valid_patient_identifier


def test_valid_patient_identifier():
    valid, message = is_valid_patient_identifier("12345678")
    assert valid is True
    assert message is None


def test_rejects_non_numeric_identifier():
    valid, message = is_valid_patient_identifier("abc12345")
    assert valid is False
    assert "numeric" in message


def test_rejects_short_identifier():
    valid, message = is_valid_patient_identifier("1234567")
    assert valid is False
    assert "8 and 10" in message


def test_rejects_identical_digits():
    valid, message = is_valid_patient_identifier("11111111")
    assert valid is False
    assert "identical" in message


def test_accepts_ten_digit_identifier():
    valid, message = is_valid_patient_identifier("1234567890")
    assert valid is True
    assert message is None


def test_rejects_too_long_identifier():
    valid, message = is_valid_patient_identifier("12345678901")
    assert valid is False
    assert "8 and 10" in message