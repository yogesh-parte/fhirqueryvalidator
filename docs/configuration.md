# Configuration Guide

Operators and developers configure the FHIR Search Validator via environment variables. Secrets are never committed — use `config/.env.local` (gitignored).

## Quick setup

```bash
cp config/.env.example config/.env.local
```

Edit `config/.env.local` as needed. The validator loads this file automatically via `FhirValidatorService.from_env()`.

## Environment variables

| Variable | Default | Required | Description |
|----------|---------|----------|-------------|
| `FHIR_DEFAULT_SERVER_KEY` | `hapi` | No | Preset public server: `hapi`, `firely`, `spark`, `wildfhir` |
| `FHIR_METADATA_URL` | (from preset) | No | Override CapabilityStatement URL |
| `FHIR_SERVER_BASE` | (from preset) | No | Override FHIR server base URL |
| `FHIR_USE_AUTH` | `false` | No | Enable OAuth client-credentials (`true`/`1`/`yes`) |
| `TOKEN_URL` | — | If auth enabled | OAuth token endpoint |
| `CLIENT_ID` | — | If auth enabled | OAuth client ID |
| `CLIENT_SECRET` | — | If auth enabled | OAuth client secret |
| `FHIR_CAPABILITY_CACHE_ENABLED` | `true` | No | Enable in-memory CapabilityStatement cache |
| `FHIR_CAPABILITY_CACHE_TTL_SECONDS` | `86400` | No | Cache TTL in seconds (24 hours) |

## CapabilityStatement cache

The validator caches `/metadata` responses in-memory to reduce network calls when validating multiple queries against the same server within a single process.

```env
FHIR_CAPABILITY_CACHE_ENABLED=true
FHIR_CAPABILITY_CACHE_TTL_SECONDS=86400
```

| Setting | Effect |
|---------|--------|
| `FHIR_CAPABILITY_CACHE_ENABLED=false` | Every `load_capability_statement()` call fetches fresh metadata |
| `FHIR_CAPABILITY_CACHE_TTL_SECONDS=0` | Entries expire on the next read (no effective reuse across calls) |
| Shorter TTL (e.g. `3600`) | Refresh metadata at most once per hour |

### Trigger-based invalidation

Invalidate cache programmatically when you know server capabilities have changed:

```python
from fhir_validator_agent import invalidate_capability_cache, FhirValidatorService

# Drop cache for one server
invalidate_capability_cache("https://hapi.fhir.org/baseR4/metadata")

# Or refresh a running service
service = FhirValidatorService.from_env()
service.refresh_capability()
```

Cache is **per-process**. Restarting Python clears all entries. Entries with different `Authorization` headers are cached separately.

## Public test servers (no authentication)

Built-in presets require **no credentials**. See [public-test-servers.md](public-test-servers.md).

```env
FHIR_DEFAULT_SERVER_KEY=hapi
FHIR_USE_AUTH=false
```

### HAPI FHIR R4 (default)

```env
FHIR_DEFAULT_SERVER_KEY=hapi
```

Equivalent URLs:

- Metadata: `https://hapi.fhir.org/baseR4/metadata`
- Base: `https://hapi.fhir.org/baseR4`

### Firely

```env
FHIR_DEFAULT_SERVER_KEY=firely
```

### Spark

```env
FHIR_DEFAULT_SERVER_KEY=spark
```

### WildFHIR Community

```env
FHIR_DEFAULT_SERVER_KEY=wildfhir
```

## Custom server

Point to any FHIR R4 server by overriding URLs:

```env
FHIR_METADATA_URL=https://my-server.example/fhir/metadata
FHIR_SERVER_BASE=https://my-server.example/fhir
FHIR_USE_AUTH=false
```

## OAuth client-credentials

For protected metadata endpoints:

```env
FHIR_USE_AUTH=true
TOKEN_URL=https://auth.example.com/oauth/token
CLIENT_ID=your-client-id
CLIENT_SECRET=your-client-secret
```

If `FHIR_USE_AUTH=true` but `TOKEN_URL`, `CLIENT_ID`, or `CLIENT_SECRET` is missing, the validator raises a clear error when fetching auth headers.

## Troubleshooting

### Metadata unreachable

```text
requests.exceptions.ConnectionError ...
```

- Check network connectivity and firewall rules
- Verify `FHIR_METADATA_URL` is correct
- Public sandboxes may be intermittently down — try another preset key

### JSON decode error on metadata

Some servers return XML unless `Accept: application/fhir+json` is sent. The built-in client handles this automatically.

### OAuth failures

```text
RuntimeError: Missing OAuth configuration: TOKEN_URL, CLIENT_ID, CLIENT_SECRET
```

Ensure all three OAuth variables are set when `FHIR_USE_AUTH=true`.

```text
requests.exceptions.HTTPError: 401
```

Verify client credentials and token URL with your identity provider.

### Wrong server selected

Confirm active environment:

```python
from fhir_validator_agent.config.settings import resolve_fhir_urls
print(resolve_fhir_urls())
```

## Security practices

- Never commit `config/.env.local` or files containing secrets
- Use `config/.env.example` as the documented template only
- Do not send PHI to public test sandboxes
- Rotate OAuth client secrets if exposed