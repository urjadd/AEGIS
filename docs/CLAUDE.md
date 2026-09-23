# AEGIS Platform: Claude Code Project Memory

This file gives Claude Code persistent context about the AEGIS codebase so you can work effectively across sessions without re-explaining the architecture every time.

---

## What This Project Is

AEGIS is a 9-service enterprise AI governance platform. It is not a single app. Each service is independently deployable, has its own PostgreSQL database, and communicates via internal API keys or MCP tool calls. The investigation agent is the only Claude-powered autonomous component.

---

## Service Map

| Service | Port | Purpose |
|---------|------|---------|
| api-gateway | 8000 | Single entry point, JWT validation, rate limiting, correlation IDs |
| auth-service | 8001 | Users, roles, JWT issuance, RBAC permissions |
| usecase-onboarding-service | 8002 | AI use case lifecycle, compliance check workflow |
| rag-engine | 8003 | Document ingestion, retrieval, generation, MCP server |
| fraud-detection-service | 8004 | XGBoost model serving, rule engine, alerts, MCP server |
| investigation-agent-service | 8005 | Claude Agent SDK agentic loop, MCP tool calls |
| token-metering-service | 8006 | LLM usage tracking, budget enforcement |
| audit-service | 8007 | Append-only event log |
| notification-service | 8008 | Email, Slack, webhook notifications |

---

## Key Conventions

**Every service must have:**
- `/health` endpoint (process alive)
- `/ready` endpoint (dependencies connected)
- Structured JSON logging with `correlation_id`, `service_name`, `user_id`
- Pydantic `BaseSettings` for config (no hardcoded values)
- Alembic migrations in `alembic/versions/`
- OpenAPI spec exported to `docs/api/{service-name}.yaml`

**All LLM calls must:**
- Go through the token metering service first (check budget)
- Return structured JSON (not free-text): use JSON schema enforcement
- Log to audit service after completion
- Mask PII via Presidio before the call

**Prompt templates:**
- Live in `shared/prompts/` as versioned `.txt` files
- Use XML tags: `<context>`, `<policy>`, `<query>`, `<output_format>`
- Include few-shot examples for classification tasks
- Never hardcode prompts inside service code

---

## MCP Servers

Two services run MCP servers in addition to their REST APIs.

**RAG Engine MCP (stdio transport):**
- `rag_retrieve(query: str, filter: dict) -> list[Chunk]`
- `rag_generate(query: str, chunks: list[Chunk]) -> GenerationResult`
- `rag_check_compliance(use_case: dict) -> ComplianceResult`

**Fraud Detection MCP (stdio transport):**
- `fraud_predict(transaction: Transaction) -> PredictionResult`
- `fraud_get_alert(alert_id: str) -> Alert`
- `fraud_similar_cases(features: dict, limit: int) -> list[Case]`

Tool schemas live in `shared/contracts/mcp_schemas.py`. Keep tool surface minimal: only expose fields the agent actually needs.

---

## Investigation Agent

Lives in `services/investigation-agent-service/`. Uses Claude Agent SDK.

**Agent loop:**
1. Receive fraud alert ID
2. Call `fraud_get_alert` to assemble transaction context
3. Call `rag_retrieve` to get relevant SOPs
4. Call `fraud_similar_cases` to find patterns
5. Synthesize investigation summary
6. Run evaluator-optimizer: check summary against rubric, re-run if score below threshold
7. If case is ESCALATED: spawn subagent for deeper regulatory retrieval
8. Present recommendation to analyst for sign-off
9. Call `case_update` only after analyst approves

**Permission sandbox:**
- Agent cannot write to audit log directly (audit service listens on events)
- Agent cannot approve its own resolutions
- Agent token budget is separate from other services

---

## Common Commands

```bash
make up               # Start all services
make down             # Stop all services
make build            # Rebuild Docker images
make test             # Run all tests
make migrate          # Run Alembic migrations for all services
make seed             # Load sample docs, fraud data, user accounts
make logs             # Tail all logs
make logs service=rag-engine   # Tail a specific service
make lint             # Linting and type checks
```

---

## Database

Each service has its own PostgreSQL database. Connection strings follow the pattern:
`postgresql://aegis_{service}:password@postgres/{service}_db`

Init scripts in `infrastructure/postgres/` create databases and users on first run.

---

## Environment Variables

Copy `.env.example` to `.env`. Required variables:
- `ANTHROPIC_API_KEY`: Claude API key for RAG engine and investigation agent
- `QDRANT_URL`: Qdrant vector database URL
- `REDIS_URL`: Redis for Celery and pub/sub
- `JWT_SECRET`: Shared secret for JWT signing
- `INTERNAL_API_KEY`: Service-to-service auth key

---

## What Not to Touch

- `audit-service/`: Append-only. Never add UPDATE or DELETE queries here.
- `shared/contracts/`: Shared Pydantic models used across services. Changes here affect all services.
- `shared/prompts/`: Versioned prompt templates. Update via new version files, do not edit existing ones.
