---
name: industry-security-standards
description: >
  Industry-standard security requirements for Go/Kubernetes cloud-native services.
  Sourced from OWASP, NIST, CIS, SLSA, GDPR, and CVSS. Fully vendor-neutral.
  Use when reviewing PRs, designing features, auditing code, or onboarding engineers.
  No organisational-specific tooling references.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags:
      - security
      - owasp
      - nist
      - cis
      - kubernetes
      - go
      - gdpr
      - devsecops
    related_skills:
      - musketeers-review
      - requesting-code-review
---

# Industry Security Standards — Go / Kubernetes Cloud Services

Standards referenced: OWASP Top 10, OWASP ASVS v4, OWASP WSTG, NIST SP 800-53/63B/207,
CIS Benchmarks (Docker, Kubernetes), SLSA, CVSS v3.1, GDPR, SANS CWE Top 25.

---

## 1. Secure Against Untrusted Input

### Injection (OWASP A03:2021 / CWE-89/78/77)
Any software passing untrusted input into an interpreter, DB, query engine, OS, or command
processor is vulnerable.

Go/K8s implementation:
- Parameterised queries only — never string-concatenate user data into SQL/NoSQL/LDAP queries
- Validate and allowlist label selectors, namespace names, annotation values before K8s API calls
- Never pass user-supplied data to `os/exec`; if unavoidable use an allowlist and never `sh -c`
- Log injection: sanitise log fields — strip or escape newlines before structured log output
- For LLM/AI features: sanitise prompt inputs; treat model output as untrusted (OWASP LLM Top 10 LLM01)

### No Backdoors or Hidden Mechanisms (CWE-506 / NIST SI-3)
- No hardcoded credentials, bypass flags, or undocumented admin endpoints in any environment
- All dependencies scanned for embedded malicious code (SCA tooling in CI)
- Secret scanning on every commit prevents accidental credential exposure

### Memory Safety (CWE-119 family)
Go is memory-safe by default. Remains relevant when:
- Using `unsafe` package — document and review every call site
- Calling C libraries via CGo — audit for buffer overflows
- Run `govulncheck` and a static analyser (gosec) in CI

---

## 2. Secure Communications

### Encryption in Transit (NIST SP 800-52 / TLS RFC 8446)
- All network communication must use TLS 1.2 minimum; TLS 1.3 preferred
- No plaintext fallback for production traffic carrying data
- Verify TLS certificates: full chain, hostname (CN/SAN); never `InsecureSkipVerify: true`
- Cipher suites: disable RC4, 3DES, export-grade; prefer ECDHE + AES-GCM
- Mutual TLS (mTLS) for service-to-service calls where the platform supports it (e.g. service mesh)
- Exception pattern: OTel OTLP export to a local DaemonSet on the node IP (port 4318, plain HTTP,
  cluster-internal loopback) is an accepted operational pattern — restrict via egress NetworkPolicy

### Cookies (OWASP Session Cheat Sheet / RFC 6265)
Session and auth cookies must carry:
- `Secure` — HTTPS only
- `HttpOnly` — no JavaScript access
- `SameSite=Strict` or `Lax` — CSRF protection

---

## 3. Identity, Authentication, and Session Management

### Authentication (NIST SP 800-63B / OWASP ASVS V2)
- Use standard protocols: OAuth 2.0, OIDC, SAML 2.0 — never build custom auth
- Service-to-service: short-lived tokens (OIDC workload identity) or mTLS; never basic auth
- No static long-lived API keys for automated processes; rotate all credentials regularly

### Password Requirements (NIST SP 800-63B §5)
- Minimum 12 characters; no complexity rules required per NIST but block known-bad passwords
- Hash with bcrypt (cost ≥ 12) or Argon2id; never MD5/SHA1 for password storage
- Brute-force protection: rate-limit or lockout after repeated failures
- Never transmit passwords in query params, logs, or HTTP GET requests

### X.509 Certificate Handling (RFC 5280)
- Validate full certificate chain and hostname on every outbound TLS connection
- Reject expired, revoked (check CRL/OCSP), or self-signed certs in production
- Automate rotation with cert-manager or equivalent; alert ≥30 days before expiry

### Session Management (OWASP ASVS V3)
- Session IDs: ≥128 bits of entropy, never in URLs
- Invalidate sessions on logout, privilege change, and inactivity timeout
- Do not reuse session IDs after re-authentication

---

## 4. Authorisation

### Least Privilege (NIST SP 800-53 AC-6 / CIS Control 6)
- Grant only the exact permissions required for each workload; review and prune regularly
- Kubernetes RBAC: no wildcard verbs (`*`) on sensitive resources; explicit resource lists
- Prefer namespaced Role over ClusterRole where possible
- `automountServiceAccountToken: false` unless the workload explicitly needs it

### Prevent Privilege Escalation (CWE-269)
- Validate request identity and scope before acting; never trust caller-supplied tenant/owner identifiers
  without verifying against an authoritative source
- Pod containers: `allowPrivilegeEscalation: false`

### Fine-Grained Authorisation
- For multi-tenant systems: enforce tenant isolation at every data access point; one tenant's request
  must not affect or reveal another tenant's data (OWASP AIDOR / OWASP A01:2021)

---

## 5. Secrets and Credential Management

### Secure Storage (OWASP Top 10 A02:2021 / NIST SP 800-57)
- Secrets (tokens, API keys, TLS private keys, DB passwords) must be stored encrypted at rest
- Never in: plaintext files, version control, container images, ConfigMaps, env vars visible in pod specs
- Use a secrets manager (Vault, AWS Secrets Manager, GCP Secret Manager, K8s ExternalSecrets)
- Mount secrets as files (tmpfs volumes); prefer over environment variables

### Rotation and Lifecycle
- Rotate all credentials on a regular schedule and immediately on suspected compromise
- Short-lived credentials preferred over long-lived static tokens
- Track expiry; alert before expiry rather than reacting after

### Go-Specific
- Use `crypto/rand` for all security-sensitive random values; never `math/rand`
- Use `crypto/sha256+` for hashing; never `crypto/md5` or `crypto/sha1` for security purposes
- Zero sensitive data from memory after use where the data is particularly sensitive (e.g. private keys)

---

## 6. Denial-of-Service and Resource Limits

### Protection (OWASP Top 10 A07 / CWE-400)
- Bound all queue/channel sizes: never unbounded in-memory accumulation
- Paginate all K8s list calls: `client.Limit(N)` + `Continue` token — never materialise a full
  unbounded UnstructuredList
- Bound message queue consumers: limit in-flight messages (count + bytes) per subscriber
- Apply rate-limiting and backpressure on all public APIs and async consumers
- K8s resource limits (CPU + memory) on every container; no uncapped `limits: {}`
- Set `GOMEMLIMIT` to ~80% of the container memory limit for Go processes

---

## 7. Information Disclosure

### Prevent Leakage (OWASP A05:2021 / CWE-200)
- Never expose internal stack traces, error bodies, or system details to external callers
- Return generic error messages to API clients; full detail only in structured server-side logs
- Never log full error chains (`%+v`) in hot paths — allocates errorVerbose strings under load
- Scrub tokens, passwords, personal data before logging; log only safe structural metadata
- OTel trace spans: do not add attributes containing personal data or internal identifiers

---

## 8. Container and Runtime Security

### Container Hardening (CIS Docker Benchmark / NSA K8s Hardening Guide)
- Base image: distroless or scratch — no shell, no package manager, minimal attack surface
- `runAsNonRoot: true`
- `allowPrivilegeEscalation: false`
- `capabilities.drop: ["ALL"]` — add back only what is explicitly required
- `seccompProfile.type: RuntimeDefault`
- Read-only root filesystem where possible
- `hostPID: false`, `hostNetwork: false` unless operationally required and documented
- No secrets in environment variables visible in pod specs; use volume mounts

### Image Supply Chain (SLSA / CIS)
- Pin base image tags to digest (e.g. `image@sha256:...`), not mutable tags
- Source images from a trusted registry; no ad-hoc public registry pulls in production
- Sign images where the platform supports it (Sigstore/cosign, Notary)

### Kubernetes Pod Security (CIS K8s Benchmark)
- Enforce Pod Security Standards (`restricted` profile) on all namespaces
- NetworkPolicy for every workload: explicit ingress and egress rules; default-deny
- Disable default service account token automounting
- Resource quotas on all namespaces

---

## 9. Secure Software Development Lifecycle (SSDLC)

### Threat Modeling (STRIDE / OWASP Threat Modeling)
- Perform threat modeling for every new service and material change to an existing one
- STRIDE: Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, Elevation of Privilege
- Feed findings into the issue tracker as security tasks; track to closure

### Secure Coding (SANS CWE Top 25 / OWASP Secure Coding Practices)
Go:
- `gosec` in CI; address G304 (path traversal), G401 (MD5/SHA1), G501 (unsafe crypto)
- Handle all errors explicitly; never `_ = err` for security-relevant operations
- Use `context.Context` for cancellation propagation; never `context.Background()` in goroutines
  that should respect graceful shutdown
- Validate all struct inputs at trust boundaries

Kubernetes YAML:
- Pod Security Standards: `restricted` profile
- No wildcard RBAC; version-control all RBAC manifests alongside code

### Code Review (OWASP SAMM / NIST SA-11)
- All code reviewed before merging; security-sensitive changes require explicit security sign-off
- Branch protection: no direct push to default branch; PRs with at least one reviewer required
- Automated checks (lint, tests, security scan) must pass before merge

### Security Scanning in CI (OWASP DevSecOps / SLSA)

| Scan type            | Example tools                 | Fail on                     |
|----------------------|-------------------------------|-----------------------------|
| Static analysis      | gosec, semgrep, CodeQL        | Critical / High severity    |
| Dependency SCA       | govulncheck, Renovate         | Known CVE in direct dep     |
| Container scan       | Trivy, Grype                  | Critical CVE in base image  |
| Secret scanning      | gitleaks, truffleHog          | Any credential in source    |
| License scan         | FOSSA, licensee               | Copyleft in proprietary product |
| SBOM generation      | syft, cdxgen                  | On every release            |

### Vulnerability Patch SLAs (CVSS v3.1)

| CVSS Score | Patch SLA    |
|------------|--------------|
| 9.0 – 10.0 | 24 hours     |
| 7.0 – 8.9  | 7 days       |
| 4.0 – 6.9  | 30 days      |
| 0.1 – 3.9  | 90 days      |

Use Renovate or Dependabot to automate dependency updates and stay within SLAs.

### CI/CD Pipeline Security (SLSA / CNCF Supply Chain Security)
- Pin all third-party CI actions/plugins to a commit digest, not a mutable tag
- Least-privilege CI tokens: `contents: read` by default; grant write only where needed
- No secrets in pipeline YAML; inject via secrets manager or CI secret store
- Separate staging and production pipelines; require an approval gate before production deploy
- Treat the pipeline definition as code: version-controlled, reviewed, tested

### Software Composition Analysis and SBOM (NTIA / SPDX / CycloneDX)
- Maintain an accurate Software Bill of Materials for every release
- All third-party components: license-compatible, no unpatched Critical/High CVEs at release
- Track all dependencies in a dependency management file (go.mod, package.json, etc.)

---

## 10. Operational Security

### Security Monitoring (NIST SP 800-137 / CIS Control 6)
Monitor and alert on:
- Authentication failures and unusual access patterns
- Authorisation denials (RBAC, policy engine)
- Container OOM kills and crash loops
- Certificate expiry (alert ≥30 days in advance)
- Unexpected outbound network connections

### Secure Configuration Management (CIS Control 4)
- All configuration version-controlled and reviewed
- Environment separation: dev/staging/prod configs never share secrets
- Changes deployed via automated pipeline (GitOps preferred); no manual production changes
- Immutable infrastructure where possible; changes via redeploy, not in-place mutation

### Incident Response (NIST SP 800-61)
- Document and test an incident response plan before you need it
- Assign incident severity using CVSS; define escalation paths and response time targets
- Patch and redeploy within the CVSS SLA table above; post-incident review for Critical events

---

## 11. Data Protection and Privacy

### Data Minimisation and Classification (GDPR Art 5 / ISO 27001 A.8.2)
- Classify all data: Public / Internal / Confidential / Restricted
- Collect only the minimum data necessary for the stated purpose
- Do not log, trace, or emit in metrics any personally identifiable information (PII)

### Data Subject Rights (GDPR Art 15–17)
For systems processing personal data:
- Support Right to Access (export), Right to Erasure, Right to Rectification
- Implement retention limits and automated deletion at end of retention period

### Purpose Limitation (GDPR Art 5(1)(b))
Data collected for one purpose must not be repurposed without renewed consent.

### Cross-Border Transfers (GDPR Chapter V)
Personal data must not leave its designated data region without a valid legal transfer mechanism
(SCCs, adequacy decision, BCRs).

---

## Pre-PR Security Checklist

```
AUTHENTICATION & AUTHORISATION
[ ] No hardcoded credentials, tokens, or passwords anywhere in the changeset
[ ] Service identity uses short-lived credentials (OIDC / mTLS / workload identity)
[ ] RBAC grants are minimal and explicit — no wildcards
[ ] Multi-tenant isolation enforced at every data access point

INPUT & INJECTION
[ ] All untrusted input validated/allowlisted before passing to interpreters or APIs
[ ] No user-controlled data in log fields without sanitisation

ENCRYPTION
[ ] All outbound connections use TLS with certificate validation
[ ] InsecureSkipVerify: false everywhere

CONTAINERS
[ ] Distroless or equivalent minimal base image
[ ] runAsNonRoot, allowPrivilegeEscalation:false, capabilities.drop:ALL, seccompProfile:RuntimeDefault
[ ] Resource limits (CPU + memory) set on every container

RESOURCE SAFETY
[ ] All K8s list calls paginated (Limit + Continue)
[ ] All async consumers have bounded in-flight queue sizes
[ ] context.Context propagated to goroutines; no context.Background() in long-lived paths

LOGGING & PRIVACY
[ ] No PII, secrets, or full error chains in log output
[ ] Error responses to callers are generic; detail stays server-side

CI/CD
[ ] Secret scanning passing (no credentials committed)
[ ] Third-party actions/plugins pinned to digest
[ ] Dependency scan passing (no Critical CVEs)
[ ] SBOM updated if new dependencies added

DOCUMENTATION
[ ] Threat model updated if attack surface changed
[ ] Security-relevant operational notes in README / runbook
```

---

## Common Code Review Findings (Go / Kubernetes)

| Finding                                         | Standard           | Severity |
|-------------------------------------------------|--------------------|----------|
| Unbounded K8s List (no Limit)                   | CWE-400            | High     |
| Async consumer always Acks regardless of error  | CWE-400            | High     |
| `context.Background()` in cleanup goroutine     | NIST SI-2 / CWE    | High     |
| Full error chain logged (`%+v` / errorVerbose)  | CWE-200            | Medium   |
| PII or payload logged verbatim                  | GDPR / CWE-532     | High     |
| Shared mutable state without synchronisation   | CWE-362 (race)     | High     |
| Secret in ConfigMap / env var plaintext         | CWE-312            | Critical |
| `InsecureSkipVerify: true`                      | CWE-295            | Critical |
| Wildcard RBAC verb `*`                          | CIS K8s / AC-6     | High     |
| No resource limits on container                 | CWE-400            | Medium   |
| Base image not minimal/distroless               | CIS Docker         | Medium   |
| CI action not pinned to digest                  | SLSA / CWE-494     | High     |
| Exported field bypasses synchronisation         | CWE-362            | High     |
| `crypto/md5` or `math/rand` for security use    | CWE-327 / CWE-338  | High     |

---

## References

- OWASP Top 10: https://owasp.org/Top10/
- OWASP ASVS v4: https://owasp.org/www-project-application-security-verification-standard/
- OWASP LLM Top 10: https://owasp.org/www-project-top-10-for-large-language-model-applications/
- NIST SP 800-53: https://csrc.nist.gov/publications/detail/sp/800-53/rev-5/final
- NIST SP 800-63B: https://pages.nist.gov/800-63-3/sp800-63b.html
- CIS Kubernetes Benchmark: https://www.cisecurity.org/benchmark/kubernetes
- CIS Docker Benchmark: https://www.cisecurity.org/benchmark/docker
- SLSA Framework: https://slsa.dev/
- SANS CWE Top 25: https://www.sans.org/top25-software-errors/
- GDPR full text: https://gdpr-info.eu/
- govulncheck: https://pkg.go.dev/golang.org/x/vuln/cmd/govulncheck
- gosec: https://github.com/securego/gosec
