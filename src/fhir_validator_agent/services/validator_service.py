from typing import Any

from ..config.settings import get_auth_config, load_env_file, resolve_fhir_urls
from ..core.validator import FhirQueryValidator
from ..infrastructure.capability_cache import invalidate_capability_cache
from ..infrastructure.capability_index import get_auth_headers, load_capability_statement


class FhirValidatorService:
    def __init__(
        self,
        metadata_url: str,
        server_base: str,
        use_auth: bool = False,
        token_url: str = "",
        client_id: str = "",
        client_secret: str = "",
    ):
        self.metadata_url = metadata_url
        self.server_base = server_base
        self.use_auth = use_auth
        self.token_url = token_url
        self.client_id = client_id
        self.client_secret = client_secret
        self.headers = get_auth_headers(use_auth, token_url, client_id, client_secret)
        self.cap_json = load_capability_statement(metadata_url, headers=self.headers)
        self.validator = FhirQueryValidator(self.cap_json)

    def validate_query(self, query_url: str) -> dict[str, Any]:
        resource_type, query_params = self.validator.parse_fhir_query(query_url)
        if not resource_type:
            return {"valid": False, "errors": ["Unable to parse resource type from query URL."]}
        if not self.validator.validate_resource_type(resource_type):
            return {"valid": False, "errors": [f"Resource type '{resource_type}' is not supported."]}
        errors = self.validator.validate_fhir_query(resource_type, query_params)
        return {"valid": not bool(errors), "errors": errors}

    def refresh_capability(self) -> None:
        invalidate_capability_cache(self.metadata_url)
        self.cap_json = load_capability_statement(self.metadata_url, headers=self.headers)
        self.validator = FhirQueryValidator(self.cap_json)

    @classmethod
    def from_env(cls) -> "FhirValidatorService":
        load_env_file()
        metadata_url, server_base = resolve_fhir_urls()
        use_auth, token_url, client_id, client_secret = get_auth_config()
        return cls(metadata_url, server_base, use_auth, token_url, client_id, client_secret)