# AMC CivicAI — Autonomous Civic Complaint Agent

> Zero-bureaucracy civic grievance resolution powered by AI image analysis, GIS ward routing, and automated SLA tracking.

![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111+-green?logo=fastapi)
![License](https://img.shields.io/badge/License-MIT-yellow)
![Tests](https://img.shields.io/badge/Tests-120+-brightgreen)
![Coverage](https://img.shields.io/badge/Coverage-90%25+-brightgreen)

---

## Problem Statement

Reporting a pothole, garbage dump, broken streetlight, or water logging means finding the right ward and department, filing the complaint, and chasing it for weeks. **Most citizens give up before filing.**

CivicAI eliminates this friction entirely: **a photo goes in → the AI classifies the issue, picks the ward and department, and files a complaint with a tracking ID — in under a second.**

---

## Architecture

```
┌────────────────────────────────────────────────────────────┐
│                    Frontend (SPA)                          │
│  index.html → Report Issue / Track / Directory             │
│  app.js → Agent Pipeline Visualizer + Chat Widget          │
└──────────────────────────┬─────────────────────────────────┘
                           │ HTTP/JSON
┌──────────────────────────▼─────────────────────────────────┐
│               FastAPI Application (main.py)                │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐       │
│  │ Security     │ │ Rate Limiter │ │ CORS         │       │
│  │ Headers MW   │ │ (Sliding     │ │ Middleware   │       │
│  │              │ │  Window)     │ │              │       │
│  └──────────────┘ └──────────────┘ └──────────────┘       │
│                                                            │
│  ┌─────────────────────────────────────────────────────┐   │
│  │           Civic Engine (4 Agent Tools)               │   │
│  │  ┌─────────────┐ ┌─────────────┐ ┌──────────────┐  │   │
│  │  │ Tool 1:     │ │ Tool 2:     │ │ Tool 3:      │  │   │
│  │  │ Vision      │ │ Ward        │ │ Department   │  │   │
│  │  │ Analyzer    │ │ Resolver    │ │ Router       │  │   │
│  │  └──────┬──────┘ └──────┬──────┘ └──────┬───────┘  │   │
│  │         │               │               │           │   │
│  │         └───────────────┴───────────────┘           │   │
│  │                         │                           │   │
│  │  ┌──────────────────────▼──────────────────────┐    │   │
│  │  │ Tool 4: Ticket Manager (In-Memory Store)    │    │   │
│  │  │ Thread-safe • LRU Eviction • AMC-format IDs │    │   │
│  │  └─────────────────────────────────────────────┘    │   │
│  └─────────────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────────────┘
```

---

## Agent Tool Chain

The core agent executes **4 sequential tool calls** for every complaint:

| Step | Tool | Description | Latency |
|------|------|-------------|---------|
| 1 | `amc.vision.classify_hazard()` | Classifies the issue from photo filename/description with SHA-256 seeded confidence scores | <1ms |
| 2 | `amc.gis.resolve_ward_polygon()` | Resolves area name or GPS coordinates to the correct AMC ward via substring matching and nearest-centroid fallback | <1ms |
| 3 | `amc.dispatch.assign_ticket()` | Routes the classified issue to the correct department with SLA timelines and field officer assignment | <1ms |
| 4 | `amc.ticket.create()` | Creates a ticket with AMC-format tracking ID, realistic timeline, and SLA deadline | <1ms |

Every tool call's latency is measured and included in the response for full agent transparency.

---

## Tech Stack

| Layer | Technology | Rationale |
|-------|-----------|-----------|
| Backend | FastAPI + Pydantic v2 | Async-first, auto-docs, strict validation |
| Frontend | Vanilla HTML/CSS/JS | Zero build step, maximum accessibility control |
| Vision AI | Deterministic mock classifier | Zero-dependency, reproducible demo |
| Data Store | In-memory OrderedDict | Thread-safe, bounded, O(1) lookups |
| Styling | CSS Custom Properties | Design token architecture, dark mode ready |
| Container | Multi-stage Docker | Non-root, minimal image, HEALTHCHECK |
| CI | GitHub Actions | Lint + test + coverage gates |

---

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the server
uvicorn app.main:app --reload --port 8000

# 3. Open the app
# → http://localhost:8000

# 4. Run tests
pytest tests/ -v --cov=app --cov-report=term-missing
```

---

## Project Structure

```
CivicAi/
├── app/
│   ├── __init__.py
│   ├── main.py               # FastAPI app factory
│   ├── config.py              # Centralized Pydantic settings
│   ├── config_data.py         # Ward & department registries
│   ├── api/
│   │   ├── routes_complaint.py  # POST /complaint/file
│   │   ├── routes_status.py     # POST /status/track
│   │   ├── routes_wards.py      # GET  /directory/wards
│   │   └── routes_health.py     # GET  /health
│   ├── civic_engine/
│   │   ├── vision_analyzer.py   # Tool 1: Image classification
│   │   ├── ward_resolver.py     # Tool 2: Ward resolution
│   │   ├── department_router.py # Tool 3: Department routing
│   │   └── ticket_manager.py    # Tool 4: Ticket lifecycle
│   └── middleware/
│       └── rate_limiter.py      # Sliding-window rate limiter
├── frontend/
│   ├── index.html             # WCAG 2.1 AA accessible SPA
│   ├── css/style.css          # Design system with tokens
│   └── js/app.js              # Client-side agent pipeline
├── tests/
│   ├── conftest.py            # Shared fixtures
│   ├── test_api.py            # API integration tests
│   ├── test_security.py       # Security hardening tests
│   ├── test_accessibility.py  # WCAG compliance tests
│   ├── test_vision_analyzer.py
│   ├── test_ward_resolver.py
│   ├── test_department_router.py
│   ├── test_ticket_manager.py
│   ├── test_config.py
│   ├── test_integration.py
│   └── test_middleware_edge.py
├── Dockerfile                 # Multi-stage, non-root
├── SECURITY.md                # Security policy
├── ACCESSIBILITY.md           # WCAG 2.1 AA statement
├── pyproject.toml             # Project metadata & tooling
├── requirements.txt           # Pinned dependencies
└── .github/workflows/ci.yml  # CI pipeline
```

---

## Security

See [`SECURITY.md`](SECURITY.md) for the full security policy, including:
- Content Security Policy (CSP)
- Rate limiting (sliding-window, per-IP)
- Input validation (Pydantic bounded fields)
- Container hardening (non-root, multi-stage)
- Secret management (env-only, no hardcoded keys)

---

## Accessibility

See [`ACCESSIBILITY.md`](ACCESSIBILITY.md) for the full WCAG 2.1 AA compliance statement, including:
- Skip navigation link
- ARIA live regions (polite + assertive)
- Full label and describedby associations
- `prefers-reduced-motion` media query
- `focus-visible` outlines
- Semantic HTML5 structure

---

## License

MIT License. See [`LICENSE`](LICENSE).
