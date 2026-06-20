STATIC_VALUESETS = {
    "Patient.gender": {"male", "female", "other", "unknown"},
    "AllergyIntolerance.verification-status": {"unconfirmed", "confirmed", "refuted", "entered-in-error"},
    "AllergyIntolerance.clinical-status": {"active", "inactive", "resolved"},
}


def is_valid_patient_identifier(identifier: str) -> tuple[bool, str | None]:
    if not identifier.isdigit():
        return False, "Identifier must be numeric only."
    if not (8 <= len(identifier) <= 10):
        return False, "Identifier must be between 8 and 10 digits."
    if len(set(identifier)) == 1:
        return False, "Identifier cannot be all identical digits."
    return True, None