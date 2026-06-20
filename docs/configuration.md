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