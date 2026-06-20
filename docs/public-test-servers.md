# Public Test Servers (No Authentication)

This project ships curated **default public FHIR R4 servers** for local development, integration tests, and manual validation. These endpoints support open read access to `/metadata` and search **without OAuth or API keys**.

> **Source:** Server list informed by the [HL7 FHIR Public Test Servers](https://confluence.hl7.org/display/FHIR/Public+Test+Servers) registry and community sandboxes commonly used for open FHIR testing ([reference discussion](https://share.google/aimode/R8g7GPLjllEy9Hjdk)).

## Default registry

Select a server with `FHIR_DEFAULT_SERVER_KEY` in `config/.env.local`:

| Key | Server | Base URL | Auth required |
|-----|--------|----------|---------------|
| `hapi` (default) | HAPI FHIR Reference Server (R4) | `https://hapi.fhir.org/baseR4` | No |
| `firely` | Firely Public Server (R4) | `https://server.fire.ly` | No |
| `spark` | Spark FHIR Reference Server (R4) | `https://spark.incendi.no/fhir` | No |
| `wildfhir` | AEGIS WildFHIR Community (R4) | `https://wildfhir.wildfhir.org/r4` | No |

## Quick usage

```bash
# Default (HAPI R4)
fhir-validate "https://hapi.fhir.org/baseR4/Patient?gender=male"

# Switch preset via environment
export FHIR_DEFAULT_SERVER_KEY=firely
fhir-validate "https://server.fire.ly/Patient?gender=male"
```

```python
from fhir_validator_agent.config.public_servers import get_public_test_servers_without_auth

for server in get_public_test_servers_without_auth():
    print(server["key"], server["base_url"])
```

## Server details

### HAPI FHIR (`hapi`)

- **Metadata:** `https://hapi.fhir.org/baseR4/metadata`
- **Use when:** Default choice; broad R4 coverage, widely used in tutorials
- **Reference:** [hapifhir.io](https://hapifhir.io/)

### Firely (`firely`)

- **Metadata:** `https://server.fire.ly/metadata`
- **Use when:** Testing against Firely Server capabilities
- **Reference:** [server.fire.ly](https://server.fire.ly/)

### Spark (`spark`)

- **Metadata:** `https://spark.incendi.no/fhir/metadata`
- **Use when:** Alternative open R4 endpoint; open-source Spark server
- **Reference:** [github.com/FirelyTeam/spark](https://github.com/FirelyTeam/spark)

### WildFHIR Community (`wildfhir`)

- **Metadata:** `https://wildfhir.wildfhir.org/r4/metadata`
- **Use when:** AEGIS community R4 sandbox with open metadata
- **Reference:** [wildfhir.wildfhir.org/r4](https://wildfhir.wildfhir.org/r4)

## Running tests against all public servers

```bash
# Integration tests (network required) — one case per registered server
pytest tests/integration/test_public_servers.py -m integration -v

# Manual multi-server script
python3 scripts/run_all_tests.py
```

## Custom servers

Override URLs directly (e.g. private sandbox with auth):

```env
FHIR_METADATA_URL=https://my-server.example/fhir/metadata
FHIR_SERVER_BASE=https://my-server.example/fhir
FHIR_USE_AUTH=true
TOKEN_URL=https://auth.example/oauth/token
CLIENT_ID=your-client-id
CLIENT_SECRET=your-client-secret
```

## Notes

- Public test servers are volunteer-operated and may be intermittently unavailable.
- `FHIR_USE_AUTH` defaults to `false` for the built-in presets — no credentials needed.
- Do not send PHI to public sandboxes.