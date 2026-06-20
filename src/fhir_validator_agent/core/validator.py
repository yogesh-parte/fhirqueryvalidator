from typing import Dict, List, Optional, Set

from .codeset_validator import STATIC_VALUESETS, is_valid_patient_identifier
from .query_parser import parse_fhir_query


class FhirQueryValidator:
    def __init__(self, cap_json: dict):
        self.cap_json = cap_json
        self.resource_search_params = self.extract_search_params()
        self.allowed_resource_types = self.extract_allowed_resource_types()

    def extract_search_params(self) -> List[dict]:
        params = []
        for rest in self.cap_json.get("rest", []):
            for resource in rest.get("resource", []):
                resource_type = resource.get("type")
                if not resource_type:
                    continue
                for param in resource.get("searchParam", []):
                    name = param.get("name")
                    if not name:
                        continue
                    extensions = param.get("extension", [])
                    modifiers = [
                        ext["valueCoding"]["code"]
                        for ext in extensions
                        if ext.get("url", "").endswith("CapabilityStatementSearchParameterModifiers")
                        and ext.get("valueCoding", {}).get("code")
                    ]
                    comparators = [
                        ext["valueCoding"]["code"]
                        for ext in extensions
                        if ext.get("url", "").endswith("CapabilityStatementSearchParameterComparators")
                        and ext.get("valueCoding", {}).get("code")
                    ]
                    params.append({
                        "resource_type": resource_type,
                        "search_param": name,
                        "modifiers": modifiers,
                        "comparators": comparators,
                    })
        return params

    def extract_allowed_resource_types(self) -> Set[str]:
        return {
            resource.get("type")
            for rest in self.cap_json.get("rest", [])
            for resource in rest.get("resource", [])
            if resource.get("type")
        }

    def parse_fhir_query(self, query_url: str) -> tuple[Optional[str], Dict[str, List[str]]]:
        return parse_fhir_query(query_url)

    def get_allowed_params(self, resource_type: str) -> Dict[str, dict[str, Set[str]]]:
        return {
            entry["search_param"]: {
                "modifiers": set(entry.get("modifiers", [])),
                "comparators": set(entry.get("comparators", [])),
            }
            for entry in self.resource_search_params
            if entry["resource_type"] == resource_type
        }

    def validate_param(self, param: str, allowed: Dict[str, dict[str, Set[str]]]) -> List[str]:
        parts = param.split(":", 1)
        param_name = parts[0]
        operator = parts[1] if len(parts) > 1 else None
        if param_name not in allowed:
            return [f"Search param '{param_name}' not allowed for resource"]
        if operator and operator not in allowed[param_name]["modifiers"] and operator not in allowed[param_name]["comparators"]:
            return [f"Modifier/comparator '{operator}' not allowed for param '{param_name}'"]
        return []

    def validate_static_values(self, resource_type: str, param_name: str, values: List[str]) -> List[str]:
        key = f"{resource_type}.{param_name}"
        allowed_values = STATIC_VALUESETS.get(key)
        if not allowed_values:
            return []
        return [
            f"Value '{value}' for '{key}' is not allowed. Allowed values: {allowed_values}"
            for value in values
            if value not in allowed_values
        ]

    def validate_resource_type(self, resource_type: Optional[str]) -> bool:
        return resource_type in self.allowed_resource_types

    def validate_fhir_query(self, resource_type: str, query_params: Dict[str, List[str]]) -> List[str]:
        allowed = self.get_allowed_params(resource_type)
        errors: List[str] = []
        for param, values in query_params.items():
            param_name = param.split(":", 1)[0]
            errors.extend(self.validate_param(param, allowed))
            errors.extend(self.validate_static_values(resource_type, param_name, values))
            if resource_type == "Patient" and param_name == "identifier":
                errors.extend(
                    f"Patient.identifier '{identifier}' invalid: {msg}"
                    for identifier in values
                    for valid, msg in [is_valid_patient_identifier(identifier)]
                    if not valid
                )
        return errors