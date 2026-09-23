# AEGIS: Enterprise AI Governance & Fraud Intelligence Platform

> A production-grade, microservices-based platform for safely onboarding, governing, and operating AI use cases at enterprise scale, with a fully realized fraud detection and compliance monitoring system powered by RAG, agentic investigation, and MCP-native tool integration.

---

## The Three Pillars

AEGIS is built on three foundational pillars that reflect how enterprises actually adopt AI in regulated environments.

### Pillar 1: RAG & Vector Database Intelligence

At the core of AEGIS is a Retrieval-Augmented Generation engine backed by a vector database (Qdrant). Enterprise policy documents, regulatory guidelines (RBI, SOX, GDPR), internal SOPs, and fraud investigation playbooks are ingested, chunked, embedded, and stored for semantic retrieval. Every AI-generated answer is grounded in actual organizational knowledge, not open-ended LLM generation. This eliminates hallucination risk in compliance-critical workflows and ensures that analysts, auditors, and business users can trust the system's outputs with full source citations.

The RAG engine also exposes its retrieval and generation capabilities as an MCP (Model Context Protocol) server, allowing the investigation agent and other Claude-powered tools to call it natively as a tool.

### Pillar 2: Enterprise Platform Approach to AI Use Case Onboarding

AEGIS is not a single AI application. It is a platform that allows multiple AI use cases to be proposed, reviewed, approved, deployed, and monitored through a governed lifecycle. Business teams submit use case requests through a self-service portal. Each request is automatically checked against stored compliance policies via the RAG engine, classified by data sensitivity, assigned token budgets, and routed through a multi-stage approval workflow (DRAFT, SUBMITTED, COMPLIANCE_REVIEW, APPROVED, DEPLOYED, RETIRED). This "platform approach" mirrors how large enterprises (banking, insurance, telecom) manage AI adoption at scale.

### Pillar 3: Data Privacy, LLM Governance & Access Control

Every interaction with an LLM is governed. PII is detected and masked before any data reaches the model. Token usage is tracked per use case, per team, per month, with hard budget limits that prevent runaway costs. Role-based access control (RBAC) ensures that a fraud analyst cannot modify compliance rules, a business user cannot access raw investigation data, and only platform administrators can approve new use cases. A complete, immutable audit trail logs every query, every model response, every access event, and every investigation action for regulatory reporting and forensic review.

---

## System Architecture

```
                                    ┌──────────────────┐
                                    │     Frontend     │
                                    │   (React + TW)   │
                                    └────────┬─────────┘
                                             │
                                    ┌────────▼─────────┐
                                    │   API Gateway    │
                                    │  (Rate Limiting, │
                                    │  JWT Validation, │
                                    │  Correlation IDs)│
                                    └────────┬─────────┘
                                             │
                 ┌───────────────────────────┬┴┬───────────────────────────┐
                 │                           │ │                           │
        ┌────────▼─────────┐    ┌────────────▼─▼──────────┐    ┌──────────▼───────┐
        │   Auth Service   │    │ Use Case Onboarding Svc │    │ Fraud Detection  │
        │  (JWT, RBAC,     │    │ (Workflow Engine,        │    │ Service (ML Model,│
        │   Permissions)   │    │  Compliance Checker)     │    │ Rule Engine,     │
        └──────────────────┘    └───────────┬──────────────┘    │ Alert Generator) │
                                            │                   └────────┬─────────┘
                                            │                            │
                                   ┌────────▼─────────┐       ┌─────────▼────────┐
                                   │    RAG Engine     │       │  Investigation   │
                                   │ (Ingestion,      │       │  Agent Service   │
                                   │  Retrieval,      │◄──────┤ (Claude Agent SDK│
                                   │  Generation,     │       │  MCP Tool Calls, │
                                   │  MCP Server,     │       │  Agentic Loop)   │
                                   │  PII Filtering)  │       └──────────────────┘
                                   └────────┬─────────┘
                                            │
                          ┌─────────────────┼─────────────────┐
                          │                 │                  │
                 ┌────────▼──────┐ ┌────────▼──────┐ ┌────────▼──────┐
                 │Token Metering │ │ Audit Service │ │ Notification  │
                 │   Service     │ │ (Immutable    │ │   Service     │
                 │ (Budget Caps, │ │  Event Log)   │ │ (Email, Slack,│
                 │  Cost Tracking│ │               │ │  Webhooks)    │
                 └───────────────┘ └───────────────┘ └───────────────┘
```

---

## Services Breakdown

### 1. API Gateway

The single entry point for all client traffic. No backend service is exposed directly.

| Capability            | Detail                                                              |
|----------------------|----------------------------------------------------------------------|
| Routing              | Path-based forwarding to internal services (`/api/v1/...`)          |
| Authentication       | JWT validation at the edge, downstream services trust the token     |
| Rate Limiting        | Per-client, per-API-key throttling                                  |
| Correlation IDs      | Generates a UUID per request, propagated to every downstream call   |
| Request Logging      | Structured JSON logs for every inbound/outbound request             |
| API Versioning       | Versioned routes to support backward compatibility                  |

**Tech:** FastAPI with custom middleware (or Kong/Traefik for an off-the-shelf option).

---

### 2. Auth Service

Owns identity, authentication, and authorization for the entire platform.

| Capability             | Detail                                                            |
|-----------------------|---------------------------------------------------------------------|
| User Management       | Registration, login, password hashing (bcrypt)                     |
| JWT Issuance          | Access tokens + refresh token rotation                             |
| Role Definitions      | PLATFORM_ADMIN, USE_CASE_OWNER, COMPLIANCE_OFFICER, FRAUD_ANALYST, VIEWER |
| Permission Matrix     | Fine-grained permissions: `usecase:create`, `rag:query`, `fraud:investigate`, `audit:read` |
| Service-to-Service Auth | Internal API keys for inter-service communication                |

**Tech:** FastAPI, PostgreSQL (users/roles/permissions tables), python-jose for JWT.

---

### 3. Use Case Onboarding Service

The platform governance layer that manages the lifecycle of every AI use case.

| Capability               | Detail                                                          |
|--------------------------|------------------------------------------------------------------|
| Use Case CRUD            | Title, description, data requirements, target LLM, owning team  |
| Workflow State Machine   | DRAFT → SUBMITTED → COMPLIANCE_REVIEW → APPROVED/REJECTED → DEPLOYED → RETIRED |
| Automated Compliance Check | On submission, async call to RAG engine checks the use case against stored regulatory policies |
| Data Classification      | Tags per use case: PUBLIC, INTERNAL, CONFIDENTIAL, RESTRICTED    |
| Use Case Passport        | Auto-generated summary: what was approved, by whom, with what constraints |
| Structured Output        | Compliance check results returned as validated JSON schema (not free-text) for downstream parsing |

**Tech:** FastAPI, PostgreSQL, Celery + Redis (async compliance check tasks).

---

### 4. RAG Engine

The technical heart of the platform. Provides grounded, cited AI answers from enterprise knowledge. Also operates as an MCP server so agentic services can call retrieval and generation as first-class tools.

| Capability                | Detail                                                          |
|--------------------------|------------------------------------------------------------------|
| Document Ingestion       | Upload PDFs/docs → text extraction (PyMuPDF) → chunking (512 tokens, 50 token overlap) → embedding → vector store |
| Retrieval API            | Semantic search with metadata filtering (e.g., "only RBI guidelines") |
| Generation API           | Retrieved chunks + user query → LLM prompt → grounded answer with source citations |
| Prompt Caching           | Repeated policy document lookups use Claude prompt caching to reduce latency and token cost |
| Structured Output        | All LLM responses enforced via JSON schema: `{answer, citations, confidence, scope_check}` |
| XML Tag Architecture     | System prompts use explicit XML tags (`<context>`, `<policy>`, `<query>`) for reliable parsing |
| Few-Shot Compliance Examples | Compliance checker prompts include labeled examples of compliant vs. non-compliant use cases |
| PII Filtering            | Presidio-based detection and masking of account numbers, Aadhaar, names before LLM call |
| Prompt Injection Detection | Validates user queries for injection attempts before processing |
| Output Guardrails        | Validates LLM output stays within the scope of retrieved context |
| MCP Server               | Exposes `rag_retrieve`, `rag_generate`, and `rag_check_compliance` as MCP tools over stdio transport |

**Tech:** LangChain, Qdrant, FastAPI, Presidio, Claude API (Sonnet), MCP Python SDK.

---

### 5. Fraud Detection Service

A fully realized ML use case running on the governed platform. Also exposed as an MCP server for the investigation agent.

| Capability             | Detail                                                            |
|-----------------------|---------------------------------------------------------------------|
| Model Serving          | Pre-trained XGBoost model, `/predict` endpoint returns fraud probability + risk tier (LOW, MEDIUM, HIGH, CRITICAL) |
| Feature Engineering    | Transaction velocity, amount deviation, geo-distance, time-since-last, merchant risk score |
| Rule Engine            | Hard rules stored in DB, editable by compliance officers without redeployment (e.g., "any transaction > ₹5,00,000 from a new device = auto-flag") |
| Alert Generator        | Creates structured alert records with severity, triggers webhooks  |
| MCP Server             | Exposes `fraud_predict`, `fraud_get_alert`, and `fraud_similar_cases` as MCP tools with typed input/output schemas |

**Tech:** FastAPI, XGBoost (joblib serialized), PostgreSQL (rules + alerts), MCP Python SDK.

---

### 6. Investigation Agent Service

The analyst's AI-powered workbench, rebuilt as a Claude Agent SDK agentic loop. The agent autonomously assembles investigation context, calls tools, retrieves SOPs, and proposes resolution — the analyst reviews and approves.

| Capability              | Detail                                                           |
|------------------------|-------------------------------------------------------------------|
| Agentic Loop            | Claude Agent SDK orchestrator runs an autonomous reasoning loop: observe alert → plan → call tools → synthesize → present to analyst |
| Tool Calls via MCP      | Agent calls `rag_retrieve` (SOPs), `fraud_get_alert` (transaction context), `fraud_similar_cases` (pattern matching), `case_update` (lifecycle transitions) |
| Evaluator-Optimizer Pattern | Agent self-evaluates its investigation summary against a rubric before presenting to analyst; re-runs if confidence is below threshold |
| Subagent Delegation     | For ESCALATED cases, spawns a subagent to perform deeper document retrieval across multiple regulatory sources |
| Alert Context Assembly  | Pulls transaction details + model explanation (feature importances) |
| RAG-Assisted SOPs       | Retrieves relevant procedures: "What is the escalation policy for card-not-present fraud?" |
| Similar Case Retrieval  | Finds past cases with similar patterns for reference              |
| Case Lifecycle          | OPEN → INVESTIGATING → ESCALATED → RESOLVED_FRAUD / RESOLVED_LEGITIMATE |
| Analyst Notes           | Stores decisions, resolution codes for future model retraining    |
| Permission Sandbox      | Agent tools are scoped: cannot write to audit log directly, cannot approve its own resolution without analyst sign-off |

**Tech:** Claude Agent SDK, FastAPI, PostgreSQL, MCP tool calls to RAG Engine and Fraud Detection Service.

---

### 7. Token Metering Service

LLM cost governance, the enterprise concern most portfolio projects ignore entirely.

| Capability            | Detail                                                              |
|----------------------|----------------------------------------------------------------------|
| Usage Tracking        | Records every LLM call: timestamp, service, use case ID, user, model, prompt/completion tokens, estimated cost |
| Budget Enforcement    | Per use case, per team, per month limits. Returns `429 BUDGET_EXCEEDED` when ceiling is hit |
| Context Window Tracking | Logs context window utilization per call alongside token counts, flags calls approaching context limits |
| Dashboard API         | Usage trends, cost breakdown by team/use case, top consumers, projected monthly spend |

**Tech:** FastAPI, PostgreSQL (usage records), Redis (fast budget counter lookups).

---

### 8. Audit Service

Immutable, append-only event log for regulatory compliance and forensic review.

| Capability            | Detail                                                              |
|----------------------|----------------------------------------------------------------------|
| Event Capture         | User logins, permission changes, use case approvals, RAG queries, LLM responses, fraud alerts, investigation actions, agent tool calls, budget breaches |
| Append-Only Storage   | No updates, no deletes. Partitioned by month for query performance  |
| Query API             | Filter by time range, user, service, event type                     |

**Tech:** FastAPI, PostgreSQL (append-only events table), or Elasticsearch for advanced log search.

---

### 9. Notification Service

Decoupled, event-driven notifications across multiple channels.

| Capability            | Detail                                                              |
|----------------------|----------------------------------------------------------------------|
| Fraud Alerts          | Email to assigned analyst + Slack webhook                           |
| Approval Notifications| Email to requesting team on use case approval/rejection             |
| Budget Warnings       | Alert at 80% threshold to team leads                                |
| Compliance Violations | Urgent notification to compliance officers                          |

**Tech:** FastAPI, Redis pub/sub, SMTP (or mock), webhook support.

---

## Tech Stack

| Layer                | Technology                                         |
|---------------------|-----------------------------------------------------|
| Frontend            | React, Tailwind CSS                                 |
| Backend Services    | FastAPI (Python)                                    |
| Agentic Framework   | Claude Agent SDK                                    |
| Tool Integration    | Model Context Protocol (MCP), MCP Python SDK        |
| Vector Database     | Qdrant (open source, self-hosted)                   |
| RAG Framework       | LangChain / LlamaIndex                              |
| LLM                 | Claude API (Sonnet) with prompt caching             |
| Embeddings          | OpenAI `text-embedding-3-small` or local model      |
| ML Model            | XGBoost (fraud scoring)                             |
| Primary Database    | PostgreSQL (separate DB per service)                |
| Caching / Queues    | Redis (Celery broker, pub/sub, budget counters)     |
| PII Detection       | Microsoft Presidio                                  |
| Auth                | JWT + RBAC middleware                               |
| Containerization    | Docker, Docker Compose                              |
| Monitoring          | Prometheus + Grafana (pre-configured dashboards)    |
| CI/CD               | GitHub Actions                                      |

---

## Enterprise Patterns Demonstrated

Every service in this platform follows these production-grade patterns:

**Structured JSON Logging:** No `print()` statements. Every service outputs structured logs with `timestamp`, `service_name`, `correlation_id`, `user_id`, `level`, `message`, and `payload`. A single correlation ID traces a request across all services.

**Health & Readiness Endpoints:** Every service exposes `/health` (process alive) and `/ready` (dependencies connected, model loaded). Docker Compose uses these for health checks. Kubernetes-ready.

**Configuration via Environment:** No hardcoded values. Every service validates its config at startup using Pydantic `BaseSettings`. One `.env.example` documents every variable.

**Database Migrations:** Every service uses Alembic for versioned, reproducible schema migrations. `make migrate` brings any fresh database to the correct state.

**OpenAPI Specifications:** Auto-generated and exported per service. Stored in `docs/api/` for frontend integration and team onboarding.

**Consistent Error Handling:** Shared exception hierarchy (`AuthorizationError`, `ResourceNotFoundError`, `BudgetExceededError`, `ComplianceViolationError`) with a standard JSON error envelope across all services:

```json
{
  "error_code": "BUDGET_EXCEEDED",
  "message": "Monthly token budget for use case UC-2024-031 has been exhausted",
  "service": "token-metering-service",
  "correlation_id": "a1b2c3d4-e5f6-7890",
  "timestamp": "2026-05-25T20:34:00Z"
}
```

**Structured LLM Outputs:** Every LLM call in the platform returns a validated JSON schema response, not free-text. This makes outputs machine-parseable, testable, and auditable.

**Prompt Engineering Standards:** All system prompts follow a consistent pattern: XML tag structure for context separation (`<policy>`, `<context>`, `<query>`), few-shot examples for classification tasks, and explicit output format instructions. Prompts are versioned alongside code.

**MCP Tool Design:** RAG Engine and Fraud Detection Service expose capabilities as MCP servers. Tool schemas are minimal (only required fields), inputs and outputs are typed, and every tool returns a structured error on failure rather than raising an exception.

**Agentic Safety:** The Investigation Agent operates within a defined permission sandbox. It cannot modify audit records, approve its own resolutions, or exceed its token budget. Every tool call is logged to the Audit Service before execution.

**Architecture Decision Records (ADRs):** Documented trade-off decisions: why Qdrant over Pinecone, why JWT over sessions, why async events for audit logging, why MCP over direct HTTP for tool integration, why Agent SDK over custom agentic loop. Demonstrates architectural thinking, not just coding ability.

---

## Repository Structure

```
aegis-platform/
├── CLAUDE.md                 # Claude Code project memory: architecture, conventions, commands
├── services/
│   ├── api-gateway/
│   ├── auth-service/
│   ├── usecase-onboarding-service/
│   ├── rag-engine/
│   │   └── mcp_server/       # MCP server exposing rag_retrieve, rag_generate, rag_check_compliance
│   ├── fraud-detection-service/
│   │   └── mcp_server/       # MCP server exposing fraud_predict, fraud_get_alert, fraud_similar_cases
│   ├── investigation-agent-service/   # Claude Agent SDK agentic loop
│   ├── token-metering-service/
│   ├── audit-service/
│   └── notification-service/
├── shared/
│   ├── common/           # Logging, correlation IDs, health endpoints, base repos
│   ├── contracts/        # Shared Pydantic models, event schemas, MCP tool schemas
│   └── prompts/          # Versioned prompt templates with XML tag architecture
├── frontend/
│   └── src/
│       ├── pages/        # Dashboard, Onboarding, Alerts, Investigation, Audit
│       ├── components/
│       ├── hooks/
│       └── services/     # API client layer
├── infrastructure/
│   ├── docker-compose.yml
│   ├── postgres/         # Init scripts (separate DB per service)
│   ├── qdrant/
│   ├── redis/
│   ├── nginx/
│   └── monitoring/       # Prometheus config, Grafana dashboards
├── notebooks/
│   ├── 01-fraud-data-exploration.ipynb
│   ├── 02-feature-engineering.ipynb
│   ├── 03-model-training.ipynb
│   ├── 04-model-evaluation.ipynb
│   └── 05-chunking-strategy-experiments.ipynb
├── docs/
│   ├── architecture/     # System diagrams, C4, data flow, ER diagrams
│   ├── api/              # OpenAPI specs per service
│   ├── runbooks/         # Deployment, incident response, onboarding
│   └── adr/              # Architecture Decision Records
├── .github/workflows/    # CI, security scanning, staging deploy
├── Makefile              # make build, make test, make up, make seed
├── .env.example
├── README.md
└── CONTRIBUTING.md
```

---

## Quick Start

```bash
# Clone the repository
git clone https://github.com/your-username/aegis-platform.git
cd aegis-platform

# Copy environment config
cp .env.example .env

# Start all services
make up

# Run database migrations
make migrate

# Seed sample compliance docs and synthetic fraud data
make seed

# Open the platform
# Frontend:         http://localhost:3000
# API Gateway:      http://localhost:8000/api/v1
# Grafana:          http://localhost:3001
# Qdrant Dashboard: http://localhost:6333/dashboard
```

---

## Makefile Commands

| Command          | Action                                              |
|-----------------|------------------------------------------------------|
| `make up`       | Start all services via Docker Compose                |
| `make down`     | Stop all services                                    |
| `make build`    | Rebuild all Docker images                            |
| `make test`     | Run unit + integration tests across all services     |
| `make migrate`  | Run Alembic migrations for every service             |
| `make seed`     | Load sample compliance documents and fraud data      |
| `make logs`     | Tail logs (use `make logs service=rag-engine`)       |
| `make lint`     | Run linting and type checks                          |

---

## Phased Development Roadmap

| Phase   | Duration   | Deliverables                                                    |
|---------|------------|------------------------------------------------------------------|
| Phase 1 | Weeks 1-2  | RAG engine with Qdrant, document ingestion pipeline, query API, structured JSON output schema, prompt caching |
| Phase 2 | Weeks 3-4  | Auth service, use case onboarding portal, automated compliance check via RAG, XML tag prompt architecture, few-shot compliance examples, CLAUDE.md |
| Phase 3 | Weeks 5-6  | Fraud detection model, rule engine, alerting, Investigation Agent (Claude Agent SDK + MCP tool calls), MCP servers for RAG and fraud detection |
| Phase 4 | Weeks 7-8  | Token metering with context window tracking, audit logging (including agent tool calls), PII masking, Grafana dashboards, ADRs |

---

## Sample Data Included

The `make seed` command loads realistic starter data so the platform is immediately usable:

- **Compliance Documents:** Sample RBI guidelines, SOX control frameworks, GDPR data handling articles, internal fraud investigation playbooks (all synthetic/public domain)
- **Fraud Dataset:** Synthetic transaction data with realistic fraud patterns (velocity anomalies, geo mismatches, device fingerprint changes)
- **Pre-configured Rules:** Sample fraud detection rules editable through the compliance officer interface
- **User Accounts:** One account per role (admin, use case owner, compliance officer, fraud analyst, viewer) with pre-assigned permissions
- **MCP Tool Schemas:** Sample typed tool definitions for RAG and fraud detection MCP servers

---

## API Documentation

Each service auto-generates an OpenAPI specification accessible at:

```
http://localhost:{service_port}/docs      # Swagger UI
http://localhost:{service_port}/redoc     # ReDoc
```

Exported specs are stored in `docs/api/` for offline reference.

---

## Monitoring & Observability

Three pre-configured Grafana dashboards ship with the platform:

1. **Platform Health Overview:** Service uptime, request latency (p50/p95/p99), error rates, active connections per service
2. **Token Usage & Cost Tracking:** LLM token consumption by team, by use case, daily/weekly/monthly trends, projected spend, budget utilization percentages, context window utilization per call
3. **Fraud Operations:** Alert volume over time, mean time to investigate, resolution rates (fraud confirmed vs. legitimate), analyst workload distribution, agent tool call counts per investigation

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup, coding standards, PR workflow, and testing requirements.

---

## License

This project is for portfolio and educational purposes.

---

## Author

Built by [Your Name] to demonstrate enterprise AI platform architecture, agentic AI systems with Claude Agent SDK, MCP tool integration, RAG-powered intelligence, and production-grade ML deployment with full governance and compliance controls.
