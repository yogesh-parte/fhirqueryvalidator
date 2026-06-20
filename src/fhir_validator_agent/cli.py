import sys

from .services.validator_service import FhirValidatorService


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    if len(args) != 1:
        print("Usage: fhir-validate <FHIR_QUERY_URL>")
        return 1

    service = FhirValidatorService.from_env()
    result = service.validate_query(args[0])
    print(f"Valid: {result['valid']}")
    if result["errors"]:
        print("Errors:")
        for error in result["errors"]:
            print(f" - {error}")
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())