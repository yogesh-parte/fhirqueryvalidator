# OWASP Security Review — FHIR Search Validator

| Field | Value |
|-------|-------|
| **Initial review date** | 2026-06-30 |
| **Initial review time (UTC)** | 2026-06-30T14:00:00Z |
| **Remediation update (UTC)** | 2026-06-30T18:00:00Z |
| **Reviewer** | AI security review (`python-owasp-reviewer` skill) |
| **Scope** | Full repository: `src/fhir_validator_agent/`, `scripts/`, `cli`, config loading, dependencies |
| **Commit initially reviewed** | `bd297b7` (CapabilityStatement cache) |
| **Post-remediation verification** | Uncommitted local changes; 146 unit tests passing |
| **Overall risk posture (initial)** | **Low–Medium** for standalone CLI/library; **Medium** if embedded with user-controlled metadata/OAuth URLs |
| **Overall risk posture (current)** | **Low** for operator-controlled CLI/library; **Low–Medium** for multi-tenant embedding (residual DNS rebinding TOCTOU) |
| **Agentic/MCP scope** | N/A — no agent tools, MCP servers, or `SKILL.md` in this repo |

---

## 1. Executive summary

The FHIR Search Validator is a **Python library and CLI** (not a web framework app). It parses user-supplied FHIR query URLs locally and fetches CapabilityStatement metadata from configured outbound URLs. No SQL, shell execution, pickle, or template injection sinks were found in `src/`.

### Initial review (2026-06-30)

Primary concerns were **SSRF** on outbound HTTP (`load_capability_statement`, OAuth `token_url`), **dependency pinning gaps**, **bearer tokens in cache keys**, **unbounded JSON deserialization**, and missing **rate limiting** and **audit logging**.

**Initial finding counts:** High **0** · Medium **2** · Low **4** · Informational **3**

### Post-remediation (2026-06-30)

All Medium, Low, and Informational findings have been **mitigated in code**. Outbound HTTP now flows through a hardened layer (`outbound_http.py`) with URL validation, DNS resolution, IP pinning, rate limiting, response size caps, redirect blocking, and security audit logging. Dependencies are pinned with compatible-release bounds; `bandit` and `pip-audit` run in CI via `make security`.

**Current open items:** None at Medium or above. One **residual Low** risk remains: DNS rebinding TOCTOU under adversarial sub-second TTL DNS (acceptable for operator-controlled CLI; network-level SSRF filter recommended for high-risk multi-tenant hosting).

---

## 2. Architecture & trust boundaries

### Components mapped

| Component | Role | Trust boundary |
|-----------|------|----------------|
| `cli.py` / `fhir-validate` | CLI entry; accepts one query URL arg | **Untrusted:** `argv[1]` query URL (local parse only) |
| `FhirValidatorService` | Orchestrates validation | Config + query URL |
| `load_capability_statement()` | HTTP GET metadata | **Sink:** outbound HTTP (via `outbound_get`) |
| `get_auth_headers()` | OAuth client-credentials | **Sink:** outbound HTTP (via `outbound_post`) |
| `outbound_http.py` | SSRF controls, pinning, rate limit gate | Validates and executes all outbound requests |
| `url_validation.py` | Scheme/host/IP/DNS checks | Blocks private, metadata, and non-HTTPS targets |
| `rate_limit.py` | Per-host sliding window | Prevents metadata/OAuth hammering |
| `security_audit.py` | Structured security events | Logs block, rate-limit, failure, success |
| `http_limits.py` | Response size cap | Prevents OOM from oversized JSON |
| `capability_cache.py` | In-memory metadata cache | Stores JSON; hashes `Authorization` in keys |
| `config/settings.py` | Loads `config/.env.local` via dotenv | **Trusted operator** env files |
| `core/` | Parse & validate (no I/O) | Query URL params only |

### Taint analysis summary (current)

```
CLI query URL (argv)
  → parse_fhir_query()          [local parse only — no HTTP to query URL] ✓

FHIR_METADATA_URL / metadata_url / TOKEN_URL (env or constructor)
  → load_capability_statement() / get_auth_headers()
  → outbound_get() / outbound_post()
      → validate_outbound_url()       [HTTPS, blocklist, literal IP checks] ✓
      → resolve_outbound_addresses()    [DNS resolve + private IP rejection] ✓
      → pinned connection               [connect to validated IP] ✓
      → rate limiter.acquire()          [per-host window] ✓
      → read_json_response()            [size cap] ✓
      → security audit log              [block / limit / fail / success] ✓

Public API load_capability_statement(url)
  → same hardened outbound path         [SSRF mitigated for operator-controlled URLs] ✓
```

The CLI **does not** fetch the user-supplied query URL over the network. Residual SSRF risk applies only when an attacker controls DNS for an otherwise-allowed hostname (DNS rebinding TOCTOU) or when embedding the library in a service that passes **unvalidated user URLs** directly to metadata/OAuth endpoints without additional host allowlisting.

---

## 3. Automated SAST results

| Tool | Target | Result (post-remediation) |
|------|--------|---------------------------|
| **Bandit** `-r src/ -ll` | ~700 LOC (`src/fhir_validator_agent/`) | **Pass** — no Medium+ issues |
| **Bandit** `-r src/` (all severities) | Same | 1 Low (B107 false positive) |
| **pip-audit** | Installed venv / `pyproject.toml` | **No known vulnerabilities** |
| **pytest** `-m "not integration"` | Unit + regression | **146 passed** |
| **Dangerous pattern grep** | `src/**/*.py` | No `eval`, `exec`, `pickle`, `yaml.load`, `shell=True`, `verify=False` |

### Bandit detail (false positive)

| ID | Location | Note |
|----|----------|------|
| B107 | `validator_service.py:10` | Flags `client_secret: str = ""` as hardcoded password — empty default, not a secret |

`url_validation.py` includes `nosec B104` annotations on blocked-host literals (`0.0.0.0`, etc.) — these are SSRF blocklist entries, not bind addresses.

---

## 4. Findings table

### Medium — mitigated

| ID | OWASP | Title | Initial location | Status | Mitigation |
|----|-------|-------|------------------|--------|------------|
| M1 | A10 | SSRF via unconstrained metadata URL | `capability_index.py` | **Mitigated** | `validate_outbound_url()` + DNS resolve + IP pinning via `outbound_get()` |
| M2 | A10 | SSRF via OAuth token URL | `capability_index.py` | **Mitigated** | Same controls via `outbound_post()` |

### Low — mitigated

| ID | OWASP | Title | Initial location | Status | Mitigation |
|----|-------|-------|------------------|--------|------------|
| L1 | A10 | HTTP redirect following amplifies SSRF | `capability_index.py` | **Mitigated** | `allow_redirects=False` in `outbound_http.py` |
| L2 | A06 | Unpinned direct dependencies | `pyproject.toml`, `requirements.txt` | **Mitigated** | Compatible-release pins; `bandit` + `pip-audit` in CI and `make security` |
| L3 | A02 | Bearer tokens in cache key material | `capability_cache.py` | **Mitigated** | SHA-256 fingerprint for `Authorization` header values |
| L4 | A08 | Unbounded JSON response deserialization | `capability_index.py` | **Mitigated** | `read_json_response()` with `FHIR_MAX_METADATA_RESPONSE_BYTES` (default 10 MB) |

### Informational — mitigated

| ID | OWASP | Title | Initial location | Status | Mitigation |
|----|-------|-------|------------------|--------|------------|
| I1 | A04 | No outbound request rate limiting | `capability_index.py` | **Mitigated** | `rate_limit.py` — default 30 requests / 60 s per host |
| I2 | A09 | No security audit logging | `capability_index.py`, `cli.py` | **Mitigated** | `security_audit.py` — logger `fhir_validator_agent.security` |
| I3 | A05 | Legacy `requirements.txt` drift | `requirements.txt` | **Mitigated** | Notebook deps pinned with upper bounds |

### Residual — accepted

| ID | OWASP | Title | Severity | Status | Notes |
|----|-------|-------|----------|--------|-------|
| R1 | A10 | DNS rebinding TOCTOU | Low (residual) | **Accepted** | Resolve → validate → pin → connect reduces window; not eliminated for sub-second TTL DNS. Network-level SSRF filter recommended for multi-tenant hosting. |

### None identified (High)

No High-severity issues identified in scoped source code at any review stage.

### Categories largely N/A

| OWASP | Reason |
|-------|--------|
| A01 Broken Access Control | No HTTP API routes or resource IDs |
| A03 Injection | No SQL/shell/template sinks |
| A05 Misconfiguration (web) | No CORS, Swagger, or web server |
| A07 Auth Failures | OAuth delegated to external IdP; no session management in library |
| Agentic AST01–AST10 | No agents/MCP/skills in this repository |

---

## 5. Detailed findings

### [M1] — SSRF via unconstrained metadata URL — **Mitigated**

- **Initial flaw:** `load_capability_statement(url)` performed unconstrained `requests.get(url)`.
- **Exploitation (pre-fix):** Attacker-controlled `FHIR_METADATA_URL` could probe cloud metadata (`169.254.169.254`) or internal services.
- **Implementation:**

```python
# outbound_http.py — all metadata fetches
hostname, pinned_ip = select_pinned_address(url)  # url_validation.py
with _pinned_connection(hostname, pinned_ip):
    response = requests.get(url, ..., allow_redirects=False)
```

- **Controls:** HTTPS-only; hostname blocklist; literal private/reserved IP rejection; DNS resolution with per-address validation; IP pinning before connect.
- **Tests:** `test_url_validation.py`, `test_outbound_http.py`, `test_capability_index.py`

---

### [M2] — SSRF via OAuth token URL — **Mitigated**

- **Initial flaw:** `get_auth_headers()` POSTed to `token_url` without validation.
- **Exploitation (pre-fix):** Attacker-controlled `TOKEN_URL` could exfiltrate client credentials or probe internal networks.
- **Implementation:** `outbound_post()` applies the same validation, pinning, rate limiting, and logging as metadata fetches.
- **Tests:** `test_get_auth_headers_rejects_non_https_token_url`, `test_outbound_http.py`

---

### [L1] — HTTP redirect following amplifies SSRF — **Mitigated**

- **Initial flaw:** Default `allow_redirects=True` could follow 302 to internal addresses.
- **Implementation:** `allow_redirects=False` on all outbound `requests.get` / `requests.post` calls in `outbound_http.py`.
- **Tests:** `test_capability_index.py` asserts `allow_redirects=False` on mocked outbound calls

---

### [L2] — Unpinned direct dependencies — **Mitigated**

- **Initial flaw:** Open lower bounds on `requests` and `python-dotenv`; unpinned notebook deps in `requirements.txt`.
- **Implementation:**

```toml
# pyproject.toml
dependencies = [
  "requests>=2.31.0,<3",
  "python-dotenv>=1.0.1,<2",
]
```

```text
# requirements.txt (notebook legacy)
jupyter>=1.0.0,<2
google-cloud-aiplatform>=1.38.0,<2
fhirclient>=4.2.0,<5
```

- **CI:** `.github/workflows/ci.yml` runs `bandit -r src/ -ll` and `pip-audit`; `Makefile` exposes `make security`.

---

### [L3] — Bearer tokens in cache key material — **Mitigated**

- **Initial flaw:** Full `Authorization: Bearer <token>` embedded in in-memory cache keys.
- **Implementation:**

```python
# capability_cache.py
def _header_fingerprint(header_name, header_value):
    if header_name.lower() == "authorization" and header_value:
        return hashlib.sha256(header_value.encode()).hexdigest()[:16]
```

- **Tests:** `test_cache_key_does_not_store_raw_bearer_token`

---

### [L4] — Unbounded JSON response deserialization — **Mitigated**

- **Initial flaw:** `response.json()` without size cap.
- **Implementation:** `read_json_response()` rejects bodies exceeding `FHIR_MAX_METADATA_RESPONSE_BYTES` (default 10 MB).
- **Tests:** `test_http_limits.py`, `test_load_capability_statement_rejects_oversized_response`

---

### [I1] — No outbound request rate limiting — **Mitigated**

- **Implementation:** `OutboundRateLimiter` in `rate_limit.py`; configurable via:

| Variable | Default |
|----------|---------|
| `FHIR_OUTBOUND_RATE_LIMIT_PER_HOST` | `30` |
| `FHIR_OUTBOUND_RATE_LIMIT_WINDOW_SECONDS` | `60` |

- **Tests:** `test_rate_limit.py`, `test_outbound_http.py`

---

### [I2] — No security audit logging — **Mitigated**

- **Implementation:** `security_audit.py` logs to `fhir_validator_agent.security`:

| Event | Level | When |
|-------|-------|------|
| `outbound_request_blocked` | WARNING | URL validation / DNS rejection |
| `outbound_request_rate_limited` | WARNING | Rate limit exceeded |
| `outbound_request_failed` | WARNING | HTTP error / timeout |
| `outbound_request_success` | INFO | Successful metadata or OAuth fetch |

URLs are redacted (no query strings; default HTTPS port omitted).

- **Tests:** `test_security_audit.py`, `test_outbound_http.py`

---

### [R1] — DNS rebinding TOCTOU — **Accepted (residual)**

- **Risk:** Attacker with control of DNS for an allowed hostname could rotate A records between validation and a subsequent connection attempt in a different code path.
- **Current mitigation:** `select_pinned_address()` resolves, validates all returned addresses, and connects to a pinned IP in the same request flow — significantly reducing the attack window.
- **Recommended for high-risk embedding:** Network-level SSRF proxy (`ssrf-req-filter`, egress firewall) or connect only to a pre-approved host allowlist.

---

## 6. Positive observations

| Control | Evidence |
|---------|----------|
| No code injection sinks | Grep clean for `eval`, `exec`, `pickle`, `os.system`, `shell=True` |
| Secrets not in source | OAuth creds from env; `.env.local` gitignored |
| Query URL not fetched over HTTP | `validate_query()` only parses URL locally |
| HTTPS presets for public servers | `public_servers.py` uses `https://` endpoints only |
| Failed HTTP not cached | Only successful responses stored in cache |
| TLS verification default | `requests` uses `verify=True` by default (no `verify=False`) |
| Preset server registry allowlist | Unknown `FHIR_DEFAULT_SERVER_KEY` falls back to `hapi` |
| Outbound HTTP centralized | Single hardened path in `outbound_http.py` |
| DNS + IP validation | `resolve_outbound_addresses()` rejects private resolved addresses |
| Security test coverage | Dedicated tests for URL validation, HTTP limits, rate limit, audit logging, outbound HTTP |
| Automated security gates in CI | `bandit -r src/ -ll` and `pip-audit` in `.github/workflows/ci.yml` |

---

## 7. OWASP checklist summary (current)

| ID | Status | Notes |
|----|--------|-------|
| A01 | N/A | Library/CLI — no route-level access control |
| A02 | **Pass** | Env-based secrets; bearer tokens hashed in cache keys |
| A03 | **Pass** | No injection sinks |
| A04 | **Pass** | Per-host outbound rate limiting |
| A05 | **Pass** (library) | No web server misconfiguration; notebook deps pinned |
| A06 | **Pass** | Compatible-release pins; pip-audit clean |
| A07 | N/A | No end-user auth in library |
| A08 | **Pass** | JSON response size capped |
| A09 | **Pass** | Security audit logging on outbound HTTP |
| A10 | **Pass** (conditional) | SSRF mitigated for operator-controlled URLs; residual DNS rebinding TOCTOU for multi-tenant embedding |

---

## 8. Configuration reference

Security-related environment variables (see [configuration.md](../configuration.md) and `config/.env.example`):

| Variable | Default | Purpose |
|----------|---------|---------|
| `FHIR_MAX_METADATA_RESPONSE_BYTES` | `10485760` (10 MB) | Cap metadata/OAuth JSON response size |
| `FHIR_OUTBOUND_RATE_LIMIT_PER_HOST` | `30` | Max outbound requests per host per window |
| `FHIR_OUTBOUND_RATE_LIMIT_WINDOW_SECONDS` | `60` | Rate limit window in seconds |
| `FHIR_CAPABILITY_CACHE_ENABLED` | `true` | Enable in-memory CapabilityStatement cache |
| `FHIR_CAPABILITY_CACHE_TTL_SECONDS` | `86400` | Cache TTL (24 h) |

**Operator assumption:** `FHIR_METADATA_URL` and `TOKEN_URL` must be set by a trusted operator, not derived from end-user input without additional host allowlisting. Documented in [ADR 002](../adr/002-capability-statement-cache.md).

---

## 9. Verification & retest criteria

| Criterion | Status |
|-----------|--------|
| Unit tests reject non-HTTPS, loopback, metadata, and private IP URLs | ✅ |
| DNS resolution rejects hosts resolving to private addresses | ✅ |
| Outbound HTTP uses `allow_redirects=False` | ✅ |
| Outbound HTTP connects via pinned validated IP | ✅ |
| Bearer tokens not stored raw in cache keys | ✅ |
| Oversized JSON responses rejected | ✅ |
| Per-host rate limiting enforced | ✅ |
| Security events logged on block / limit / failure / success | ✅ |
| `bandit -r src/ -ll` passes | ✅ |
| `pip-audit` clean | ✅ |
| `pytest -m "not integration"` — 146 passed | ✅ |

Run locally:

```bash
make security
pytest -m "not integration"
```

---

## 10. Recommended follow-ups (optional)

| Priority | Action | When |
|----------|--------|------|
| Low | Add IdP hostname allowlist for `TOKEN_URL` (beyond HTTPS + IP checks) | When OAuth is enabled in production |
| Low | Network-level SSRF egress filter | Multi-tenant or shared-host embedding |
| Low | Commit `requirements.lock` or document `pip freeze` for notebook installs | Reproducible notebook environments |
| Info | Enable `fhir_validator_agent.security` logger in hosted deployments | Abuse detection and incident response |

---

## 11. Related documentation

- [ADR 002 — CapabilityStatement cache](../adr/002-capability-statement-cache.md)
- [Code review 2026-06-30](2026-06-30-capability-statement-cache.md)
- [Configuration guide](../configuration.md)
- [ADR index](../adr/README.md)
- [Reviews index](README.md)

---

## 12. Verdict

**Approved for operator-controlled CLI and library use.** All Medium, Low, and Informational findings from the initial review are mitigated with tests and CI gates.

**Acceptable for production embedding** in internal tooling where metadata and OAuth URLs are operator-controlled. For **multi-tenant services** that accept user-supplied server URLs, add host allowlisting and/or a network-level SSRF filter to address residual DNS rebinding TOCTOU (R1).