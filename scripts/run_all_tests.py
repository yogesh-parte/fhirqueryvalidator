#!/usr/bin/env python3
"""Run validation scenarios across all default public test servers (no auth)."""

from fhir_validator_agent import FhirValidatorService
from fhir_validator_agent.config.public_servers import get_public_test_servers_without_auth


def main():
    public_servers = get_public_test_servers_without_auth()

    test_queries = [
        {"query": "Patient?gender=male", "expected": "positive"},
        {"query": "Patient?gender=fe", "expected": "negative"},
    ]

    print(f"Testing {len(test_queries)} queries across {len(public_servers)} public servers (no auth)...\n")

    passed = 0
    failed = 0
    errors = 0

    for server in public_servers:
        print(f"--- {server['name']} ({server['key']}) ---")
        print(f"    Base: {server['base_url']}")

        try:
            service = FhirValidatorService(
                metadata_url=server["metadata_url"],
                server_base=server["base_url"],
            )

            for test in test_queries:
                print(f"\n  Query: {test['query']} (expected: {test['expected']})")
                full_query_url = f"{server['base_url']}/{test['query']}"
                result = service.validate_query(full_query_url)

                expect_valid = test["expected"] == "positive"
                actual_valid = result["valid"]
                ok = expect_valid == actual_valid

                if ok:
                    passed += 1
                    print(f"  Result: {'valid' if actual_valid else 'invalid'} — PASS")
                else:
                    failed += 1
                    print(f"  Result: {'valid' if actual_valid else 'invalid'} — FAIL")
                    for err in result["errors"]:
                        print(f"   - {err}")

        except Exception as exc:
            errors += 1
            print(f"  Error: {exc}")

        print()

    total = passed + failed + errors
    print("=" * 50)
    print(f"Summary: {passed} passed, {failed} failed, {errors} server errors")
    print(f"Total checks: {total}")
    return 1 if failed or errors else 0


if __name__ == "__main__":
    raise SystemExit(main())