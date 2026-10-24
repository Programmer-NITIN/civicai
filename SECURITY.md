# Security Policy — CivicAI

## Overview

CivicAI implements a defence-in-depth security model across all layers of the application stack. This document describes every security control, its rationale, and how it is tested.

---

## 1. HTTP Security Headers

Every response includes the following headers, enforced by middleware in `app/main.py`:

| Header | Value | Purpose |
|--------|-------|---------|
| `Content-Security-Policy` | `default-src 'self'; script-src 'self' 'unsafe-inline' ...` | Prevents XSS by restricting resource origins |
| `X-Content-Type-Options` | `nosniff` | Prevents MIME-type sniffing attacks |
| `X-Frame-Options` | `DENY` | Prevents clickjacking via iframe embedding |
| `Referrer-Policy` | `strict-origin-when-cross-origin` | Limits referrer leakage to third parties |
| `Permissions-Policy` | `camera=(), microphone=(), geolocation=(self), payment=()` | Restricts browser API access |
| `X-Permitted-Cross-Domain-Policies` | `none` | Prevents Flash/PDF cross-domain reads |
| `Strict-Transport-Security` | `max-age=63072000; includeSubDomains; preload` | Enforces HTTPS (production only) |

**Tests:** `tests/test_security.py::TestSecurityHeaders`

---

## 2. CORS Configuration

- **Debug mode:** Allows all origins (`*`) for local development convenience.
- **Production mode:** Requires explicit whitelist via `ALLOWED_ORIGINS` environment variable.
- **Allowed methods:** `GET`, `POST`, `OPTIONS` only.
- **Allowed headers:** `Authorization`, `Content-Type` only.

**Tests:** `tests/test_security.py::TestCorsConfiguration`

---

## 3. Rate Limiting

Sliding-window, per-IP rate limiting implemented in `app/middleware/rate_limiter.py`:

| Endpoint Group | Threshold | Window |
|---------------|-----------|--------|
| Complaint filing (`/complaint/*`) | 10 requests | 60 seconds |
| Status tracking (`/status/*`) | 30 requests | 60 seconds |
| Image upload (`/complaint/file-with-image`) | 5 requests | 60 seconds |

- Uses `X-Forwarded-For` header for proxy awareness.
- Returns `HTTP 429` with `Retry-After` header when exceeded.
- Backed by `collections.deque` for O(1) amortized operations.

**Tests:** `tests/test_security.py::TestComplaintRateLimit`

---

## 4. Input Validation

All request bodies use Pydantic models with strict constraints:

| Field | Constraint | Rationale |
|-------|-----------|-----------|
| `citizen_name` | 1–100 chars | Prevents empty or oversized identifiers |
| `phone` | 10–15 chars, E.164 pattern | Validates phone format |
| `area_or_address` | 2–200 chars | Bounds location input |
| `description` | Max 1000 chars | Bounds free-text input |
| `ticket_id` | 5–30 chars | Bounds token for status lookups |
| `issue_type` | Enum constraint | Only valid issue types accepted |

**Tests:** `tests/test_security.py::TestComplaintInputValidation`, `TestStatusInputValidation`

---

## 5. File Upload Security

- **Allowed MIME types:** `image/jpeg`, `image/png`, `image/webp` only.
- **Maximum file size:** 10MB (configurable via `MAX_UPLOAD_SIZE_MB`).
- **Content validation:** File content is read and size-checked before processing.
- **No file storage:** Uploaded files are processed in memory and never persisted to disk.

---

## 6. Container Security

The `Dockerfile` implements:

- **Multi-stage build:** Separates build dependencies from runtime.
- **Non-root execution:** Application runs as `appuser` (UID 10001).
- **No shell access:** Uses `CMD` with exec form.
- **Minimal image:** Based on `python:3.11-slim` with only runtime dependencies.
- **Health checks:** Built-in Docker HEALTHCHECK against `/health`.

---

## 7. Secret Management

- No secrets are hardcoded. All sensitive values are loaded from environment variables via Pydantic Settings.
- `.env` files are excluded from version control via `.gitignore`.
- `.env.example` documents all required variables with safe placeholder values.

---

## 8. AI Safety

- Vision classification uses **deterministic heuristic classification** — no model hallucination risk.
- Chat responses are **grounded** in pre-defined response templates — no generative AI used.
- All agent tool calls are **auditable** via the agent_trace field in API responses.
- System never makes autonomous decisions about emergency response or citizen safety.

---

## 9. Thread Safety

- The in-memory ticket store uses a `threading.Lock` for all read/write operations.
- Bounded to 10,000 tickets with LRU eviction to prevent memory exhaustion.
- Rate limiter stores use `collections.defaultdict(deque)` which is GIL-safe for Python.

---

## Reporting Vulnerabilities

If you discover a security issue, please email security@civicai.amc.gov.in with a description. We will acknowledge within 48 hours.
