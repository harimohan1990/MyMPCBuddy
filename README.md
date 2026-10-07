# Personal MCP Hub — Unified Personal Communication & Notification Platform

[![Python 3.13](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-14+-black.svg)](https://nextjs.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791.svg)](https://www.postgresql.org/)
[![Redis](https://img.shields.io/badge/Redis-7-DC382D.svg)](https://redis.io/)
[![MCP](https://img.shields.io/badge/MCP-Protocol-8B5CF6.svg)](https://modelcontextprotocol.io/)

A production-grade **Personal MCP Hub & Personal Digital Assistant**: one centralized, highly secure platform that connects your personal communication streams—**Gmail, Microsoft Teams, WhatsApp, Google/Outlook Calendar, GitHub**—through the **Model Context Protocol (MCP)** and unifies them into an executive inbox, AI assistant, and daily briefing center.

---

## Key Architecture & Features

### 1. Unified Multi-Provider Inbox
- Normalizes disparate messaging protocols into a unified schema:
  - `provider`, `type`, `sender`, `recipient`, `title`, `content`, `timestamp`, `priority`, `category`, `action_required`.
- **Deduplication Engine:** SHA-256 content and event hashing guarantees zero duplicate notifications across sync cycles.
- **Instant Filtering & Search:** Filter by provider, priority level (`CRITICAL`, `HIGH`, `MEDIUM`, `LOW`), unread state, or action-required status.

### 2. Model Context Protocol (MCP) Gateway
- Built around a **Tiered Permission System**:
  - `READ`: Safe read-only inspections (`search_messages`, `get_today_schedule`, `get_action_items`, `draft_email`).
  - `WRITE`: External state modifications (`send_email`, `send_teams_message`). **Requires human confirmation.**
  - `DESTRUCTIVE`: Permanent alterations (`delete_email`). **Requires human confirmation.**
- **Human-in-the-Loop Confirmation Gate:** Staged actions generate an HMAC-SHA256 signed token. Side-effects only execute upon receiving the signed cryptographic challenge.

### 3. Provider Adapter Pattern
- Clean, decoupled `CommunicationProvider` abstract base class isolating external vendor APIs.
- **Gmail Provider Adapter:** Official Google REST API integration with token refresh, inbox search, thread inspection, and message sending.
- **WhatsApp Adapter Isolation:** Strict adherence to official Meta Cloud API guidelines. Unofficial Web scraping and reverse engineering are strictly prohibited.
- **Microsoft Teams & Calendar:** Microsoft Graph API compatible models.

### 4. Zero-Trust Security & Prompt Injection Defense
- **AES-256-GCM Token Encryption:** OAuth tokens encrypted at rest with cryptographically random 96-bit initialization vectors (IVs).
- **Zero Raw Passwords:** Authentication handled solely via short-lived JWTs and OAuth 2.0 PKCE.
- **Untrusted Message Sandboxing:** External messages sanitized and isolated behind strict delimiters:
  ```text
  <<<UNTRUSTED_EXTERNAL_COMMUNICATION_BEGIN source="gmail">>>
  [Sanitized external text]
  <<<UNTRUSTED_EXTERNAL_COMMUNICATION_END>>>
  ```
- **Audit Logging:** Every automated and confirmed MCP tool invocation logged with IP, payload summary, and status.

---

## System Architecture

```text
                         ┌─────────────────────┐
                         │   WEB / MOBILE UI   │ (Next.js 14 + Tailwind)
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │     API Gateway     │ (FastAPI + Async SQLAlchemy)
                         └──────────┬──────────┘
                                    │
                   ┌────────────────┼────────────────┐
                   │                │                │
                   ▼                ▼                ▼
             Notification       AI Assistant      OAuth / Auth
                Service              │          (AES-256-GCM)
                   │                 ▼
                   │          ┌──────────────┐
                   │          │ MCP Gateway  │ (HMAC Confirmation Gate)
                   │          └──────┬───────┘
                   │                 │
          ┌────────┴─────────────────┼─────────────────┐
          │                          │                 │
          ▼                          ▼                 ▼
     Email MCP                 Teams MCP          Calendar MCP
          │                          │                 │
          ▼                          ▼                 ▼
     Gmail / Graph             Microsoft Graph     Google / Outlook
          
          ┌───────────────────────────────────────────────┐
          │                                               │
          ▼                                               ▼
     GitHub MCP                                      WhatsApp MCP
          │                                               │
          ▼                                               ▼
     GitHub API                                  Meta Cloud API Only

                    ┌─────────────────────┐
                    │     PostgreSQL 16   │
                    └─────────────────────┘

                    ┌─────────────────────┐
                    │       Redis 7       │
                    └─────────────────────┘
```

---

## Quickstart

### 1. Run with Docker Compose
```bash
# Clone and enter workspace
cd mysupport

# Copy environment variables
cp .env.example .env

# Spin up PostgreSQL 16, Redis 7, Backend, and Frontend
docker compose up --build
```
- **Web Interface:** [http://localhost:3000](http://localhost:3000)
- **API Documentation:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **Health Check:** [http://localhost:8000/health](http://localhost:8000/health)

---

### 2. Run Locally (Development)

#### Backend Setup
```bash
# Set up virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt

# Run test suite (9 unit and integration tests)
PYTHONPATH=backend pytest backend/app/tests

# Start FastAPI development server
cd backend
uvicorn app.main:app --reload --port 8000
```

#### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Open [http://localhost:3000](http://localhost:3000) in your browser.

---

### 5. Resilient Infrastructure Layer
- **Circuit Breaker Pattern:** State machine (`CLOSED`, `OPEN`, `HALF_OPEN`) with exponential backoff protects downstream communication providers from cascading failures.
- **Sliding Window Rate Limiter:** Redis-backed rate limiting with in-memory fallback.
- **Prometheus Telemetry:** Exposes `/api/v1/infra/metrics` and health diagnostics.
- **Pluggable Secrets Management:** `EnvSecretsManager` for dev and `AWSSecretsManager` with in-memory TTL caching for production.
- **Dead-Letter Job Queue:** Asynchronous provider synchronization with Redis streams.
- **Production IaC & Orchestration:**
  - **Terraform AWS:** Multi-AZ VPC, RDS PostgreSQL 16, ElastiCache Redis 7, ECS Fargate, ALB with path routing, CloudWatch.
  - **Kubernetes:** Manifests with Deployments, Services, HPAs, and Ingress with TLS.
  - **Nginx Reverse Proxy:** Rate limiting zones, security headers (CSP, HSTS), WebSocket support.
  - **GitHub Actions CI/CD:** Automated testing, linting, and Trivy security scanning.

---

## Project Structure

```text
mysupport/
├── docker-compose.yml              # Local multi-container deployment (Postgres, Redis, Backend, Frontend, Nginx)
├── .env.example                    # Environment template
├── README.md                       # Documentation
│
├── infra/                          # Cloud & Deployment Infrastructure
│   ├── terraform/                  # Production AWS Infrastructure as Code
│   │   ├── main.tf, variables.tf, outputs.tf
│   │   ├── vpc.tf                  # Multi-AZ VPC with public and private subnets
│   │   ├── rds.tf                  # Amazon RDS PostgreSQL 16 Multi-AZ with KMS
│   │   ├── elasticache.tf          # AWS ElastiCache Redis 7 Cluster
│   │   ├── alb.tf                  # Application Load Balancer with path-based routing
│   │   ├── ecs.tf                  # ECS Fargate Cluster, Task Definitions, Auto-scaling
│   │   └── cloudwatch.tf           # Log groups and alarms
│   ├── k8s/                        # Production Kubernetes Manifests
│   │   ├── configmap.yaml, secrets.yaml
│   │   ├── backend-deployment.yaml # FastAPI Deployment, Service & HPA
│   │   ├── frontend-deployment.yaml# Next.js Deployment, Service & HPA
│   │   └── ingress.yaml            # Ingress with TLS & path routing
│   └── nginx/                      # Hardened Nginx Reverse Proxy
│       └── nginx.conf              # Rate limiting, security headers, WebSocket proxy
│
├── .github/workflows/              # Continuous Integration & Delivery
│   └── ci-cd.yml                   # Automated testing, build, and Trivy security scans
│
├── backend/                        # FastAPI Application (Python 3.13+)
│   ├── Dockerfile
│   ├── pyproject.toml, requirements.txt
│   ├── alembic.ini, alembic/       # DB Migrations
│   └── app/
│       ├── main.py                 # FastAPI application
│       ├── core/                   # Security, DB, Redis, Logging, Config
│       ├── infra/                  # Application Infrastructure Layer
│       │   ├── resilience/         # Circuit Breaker & Rate Limiter
│       │   ├── telemetry/          # Prometheus metrics & latency tracker
│       │   ├── secrets/            # Pluggable Secrets Manager (Env / AWS)
│       │   └── messaging/          # Redis Job Queue & Dead-Letter Queue
│       ├── models/                 # SQLAlchemy 2 Declarative Models
│       ├── schemas/                # Pydantic v2 Schemas
│       ├── api/v1/                 # REST & SSE Route Handlers (Auth, Inbox, MCP, Infra)
│       ├── providers/              # Provider Adapter implementations (Gmail, WhatsApp, etc.)
│       ├── mcp/                    # MCP Server, Tool registry, Confirmation gate
│       ├── services/               # Normalization, Sync, Briefing, Sanitizer
│       └── tests/                  # 12 Unit and Integration tests (100% passing)
│
└── frontend/                       # Next.js 14 Application (TypeScript & Tailwind)
    ├── Dockerfile, package.json
    ├── next.config.mjs, tailwind.config.js
    └── src/
        ├── app/
        │   ├── dashboard/page.tsx  # Executive Daily Briefing & Metrics
        │   ├── inbox/page.tsx      # Unified Inbox & Message viewer
        │   ├── assistant/page.tsx  # AI Assistant with MCP tool confirmation
        │   ├── calendar/page.tsx   # Aggregated schedule & meetings
        │   ├── providers/page.tsx  # OAuth connection management
        │   ├── privacy/page.tsx    # Privacy Center & Data sovereignty
        │   └── audit/page.tsx      # Cryptographic Audit log trail
        ├── components/
        └── lib/                    # API client and TypeScript definitions
```
