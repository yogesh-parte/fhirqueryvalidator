import os
from pathlib import Path

from .public_servers import PUBLIC_TEST_SERVERS, get_public_test_server, get_server_urls

# Backward-compatible URL map derived from the public server registry.
DEFAULT_PUBLIC_SERVERS = {
    key: get_server_urls(key) for key in PUBLIC_TEST_SERVERS
}


def load_env_file(config_dir: Path | None = None) -> None:
    repo_root = Path.cwd()
    if config_dir is None:
        if not (repo_root / "config").exists():
            repo_root = repo_root.parent
        config_dir = repo_root / "config"
    env_path = config_dir / ".env.local"
    if env_path.exists():
        from dotenv import load_dotenv

        load_dotenv(env_path)


def get_default_server() -> dict[str, str]:
    default_key = os.getenv("FHIR_DEFAULT_SERVER_KEY", "hapi").lower()
    try:
        return get_server_urls(default_key)
    except KeyError:
        return get_server_urls("hapi")


def resolve_fhir_urls() -> tuple[str, str]:
    selected = get_default_server()
    metadata_url = os.getenv("FHIR_METADATA_URL") or selected["metadata_url"]
    server_base = os.getenv("FHIR_SERVER_BASE") or selected["base_url"]
    return metadata_url, server_base


def get_auth_config() -> tuple[bool, str, str, str]:
    use_auth = os.getenv("FHIR_USE_AUTH", "false").lower() in {"1", "true", "yes"}
    return (
        use_auth,
        os.getenv("TOKEN_URL", ""),
        os.getenv("CLIENT_ID", ""),
        os.getenv("CLIENT_SECRET", ""),
    )