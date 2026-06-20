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

    for server in public_servers:
        try:
            print(f"--- {server['name']} ({server['key']}) ---")
            print(f"    Base: {server['base_url']}")

            service = FhirValidatorService(
                metadata_url=server["metadata_url"],
                server_base=server["base_url"],
            )

            for test in test_queries:
                print(f"\n  Query: {test['query']} (expected: {test['expected']})")
                full_query_url = f"{server['base_url']}/{test['query']}"
                result = service.validate_query(full_query_url)

                if result["valid"]:
                    print("  Result: valid")
                else:
                    print("  Result: invalid")
                    for err in result["errors"]:
                        print(f"   - {err}")

        except Exception as exc:
            print(f"  Error: {exc}")

        print()


if __name__ == "__main__":
    main()