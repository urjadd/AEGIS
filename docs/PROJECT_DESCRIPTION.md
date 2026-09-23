# AEGIS: Project Description & Portfolio Summary

Use this document for your GitHub "About" section, LinkedIn project entry, resume bullet points, and portfolio website.

---

## One-Liner (GitHub About / Tagline)

Enterprise AI Governance & Fraud Intelligence Platform: a microservices-based system for onboarding, governing, and operating AI use cases with RAG-powered compliance, agentic fraud investigation via Claude Agent SDK, MCP-native tool integration, ML-driven fraud detection, and full LLM cost and access controls.

---

## Short Description (LinkedIn / Portfolio Card)

AEGIS is a production-grade enterprise platform that solves the real challenge organizations face when adopting AI at scale: governance. Built on three pillars, (1) RAG & Vector Database Intelligence for grounded, hallucination-free answers from internal policy documents, (2) a Platform Approach to AI Use Case Onboarding with multi-stage approval workflows and automated compliance checking, and (3) Data Privacy, LLM Token Governance & Role-Based Access Control across every AI interaction, AEGIS demonstrates what it takes to move AI from proof-of-concept to enterprise production. The platform includes a fully realized fraud detection and agentic investigation system as its showcase use case, complete with ML model serving, a configurable rule engine, a Claude Agent SDK-powered investigation agent using MCP tool calls, and real-time alerting.

---

## Detailed Description (Portfolio Page / Project Write-Up)

### The Problem

Enterprises do not struggle with building AI models. They struggle with deploying them safely. Questions like "Who approved this use case?", "What data is being sent to the LLM?", "How much are we spending on tokens?", "Does this comply with RBI/SOX/GDPR?", and "Who accessed this investigation?" are what keep CIOs, CISOs, and compliance officers up at night. Most AI portfolio projects ignore these entirely. AEGIS tackles them head-on.

### The Three Pillars

**Pillar 1: RAG & Vector Database Intelligence**
Enterprise policy documents, regulatory guidelines, and internal SOPs are ingested into a Qdrant vector database. When a business team submits a new AI use case, the system automatically retrieves and checks it against relevant compliance policies. When a fraud analyst investigates an alert, they can ask natural language questions like "What is our escalation procedure for high-value international transactions?" and receive cited, grounded answers from organizational knowledge, not generic LLM output. The RAG engine also operates as an MCP server, making its retrieval and generation capabilities available as typed, callable tools to the investigation agent.

**Pillar 2: Enterprise Platform Approach to AI Use Case Onboarding**
AEGIS is not a chatbot. It is a governed platform. AI use cases move through a formal lifecycle: DRAFT, SUBMITTED, COMPLIANCE_REVIEW, APPROVED, DEPLOYED, RETIRED. Each use case is tagged with data sensitivity classifications, assigned a token budget, and linked to an owning team. Automated compliance checks run on every submission, with results returned as validated JSON schema outputs. System prompts follow a consistent XML tag architecture for reliable parsing, and few-shot examples improve compliance classification accuracy. A "Use Case Passport" is generated for every approved use case, documenting what was approved, by whom, under what constraints. This mirrors how enterprises like banks, insurers, and telecoms manage AI adoption in practice.

**Pillar 3: Data Privacy, LLM Governance & Access Control**
PII is detected and masked (using Microsoft Presidio) before any data reaches an LLM. Token usage is metered per use case, per team, per month, with hard budget caps and context window utilization tracking. Role-based access control ensures separation of duties: fraud analysts cannot modify compliance rules, business users cannot access raw investigation data, only platform administrators can approve new use cases. An immutable, append-only audit log captures every query, every LLM response, every agent tool call, every investigation action, and every access event.

### The Showcase Use Case: Fraud Detection & Agentic Investigation

To demonstrate the platform end-to-end, AEGIS includes a complete fraud detection and agentic investigation system:

- An XGBoost model scores transactions in near real-time, using engineered features like transaction velocity, geo-distance, amount deviation, and device fingerprinting.
- A configurable rule engine (stored in the database, editable by compliance officers without code changes) layers hard business rules on top of ML predictions.
- When a transaction is flagged, a structured alert is generated with severity, model explanation (feature importances), and relevant context.
- The Investigation Agent is a Claude Agent SDK agentic loop. It autonomously observes the alert, plans an investigation, calls tools via MCP (RAG retrieval for SOPs, fraud service for transaction context and similar cases, case management for lifecycle updates), evaluates its own output against a quality rubric, and presents a recommended resolution to the analyst. For escalated cases, it spawns a subagent to perform deeper regulatory document retrieval. The analyst reviews and approves; the agent cannot close a case without sign-off.
- All agent tool calls are logged to the Audit Service before execution, and the agent operates within a permission sandbox enforced at the MCP tool layer.

### Architecture Highlights

- 9 microservices, each with its own database schema, structured logging, health/readiness endpoints, and OpenAPI spec.
- API Gateway with rate limiting, JWT validation, and correlation ID propagation for end-to-end request tracing.
- RAG Engine and Fraud Detection Service each expose an MCP server with typed tool schemas, minimal surface area, and structured error responses.
- Investigation Agent built on Claude Agent SDK with evaluator-optimizer pattern, subagent delegation, and permission-scoped tool access.
- Shared `prompts/` directory with versioned prompt templates using XML tag architecture and few-shot examples.
- Prompt caching on repeated policy document lookups in the RAG engine.
- Fully containerized with Docker Compose. One command (`make up && make seed`) starts the entire platform with sample data.
- Pre-configured Grafana dashboards for platform health, LLM token usage with context window tracking, and fraud operations metrics including agent tool call counts.
- Architecture Decision Records (ADRs) documenting trade-off decisions including: vector DB selection, auth strategy, event vs. synchronous communication, PII masking approach, MCP over direct HTTP for tool integration, Agent SDK vs. custom agentic loop.
- `CLAUDE.md` project memory file documenting the architecture, conventions, and commands for Claude Code.

---

## Tech Stack Summary (for Resume / LinkedIn Skills)

Python, FastAPI, React, Tailwind CSS, PostgreSQL, Redis, Docker, Qdrant, LangChain, XGBoost, Presidio, Celery, Prometheus, Grafana, GitHub Actions, JWT/RBAC, Claude API, Claude Agent SDK, Model Context Protocol (MCP), OpenAI API

---

## Resume Bullet Points

Pick 3 to 5 of these depending on the role you are targeting:

**For AI/ML Engineering roles:**
- Designed and built a RAG pipeline (LangChain + Qdrant) for enterprise compliance document retrieval, with PII masking, prompt injection detection, structured JSON output schemas, and XML tag prompt architecture.
- Trained and deployed an XGBoost fraud detection model with engineered features (transaction velocity, geo-distance, device fingerprinting), served via a FastAPI microservice with a configurable rule engine overlay.
- Built a Claude Agent SDK investigation agent using MCP tool calls to RAG, fraud detection, and case management services, with evaluator-optimizer loop, subagent delegation, and permission-scoped tool access.
- Implemented a token metering service tracking LLM usage and context window utilization per team and use case, with budget enforcement and cost projection dashboards.

**For Platform / Backend Engineering roles:**
- Architected a 9-service microservices platform (FastAPI, PostgreSQL, Redis, Docker) with API gateway, RBAC, correlation ID tracing, and immutable audit logging.
- Exposed RAG and fraud detection capabilities as MCP servers with typed tool schemas, minimal surface area, and structured error handling; consumed by a Claude Agent SDK agentic loop.
- Built an AI use case onboarding system with a workflow state machine, automated compliance checking via RAG, structured JSON output validation, and data sensitivity classification.
- Designed inter-service communication patterns with async event processing (Celery + Redis), service-to-service auth, and a shared structured logging framework.

**For Data Engineering / Analytics roles:**
- Built a document ingestion pipeline: PDF extraction, recursive chunking, embedding generation, and vector storage in Qdrant with metadata-filtered retrieval and prompt caching for repeated lookups.
- Designed an append-only audit event store with time-partitioned PostgreSQL tables capturing all LLM calls, agent tool calls, and investigation actions for compliance reporting.
- Created pre-configured Grafana dashboards tracking platform health, LLM token consumption with context window utilization, and fraud operations metrics including agent tool call counts per investigation.

**For Compliance / GRC-adjacent Tech roles:**
- Implemented automated regulatory compliance checking for AI use cases using RAG over RBI, SOX, and GDPR policy documents, with structured JSON output schemas and few-shot classification prompting.
- Built a governed AI use case lifecycle (DRAFT through RETIRED) with role-based approvals, data classification tagging, and auto-generated Use Case Passports.
- Designed a PII masking layer (Microsoft Presidio) ensuring no sensitive data reaches external LLMs, with full audit trail including agent tool call logs.

---

## Interview Talking Points

**"Walk me through the architecture."**
Start with the three pillars. Then explain how each pillar maps to specific services. Highlight the MCP layer: the RAG engine and fraud detection service each run an MCP server, and the investigation agent calls them as tools via the Claude Agent SDK. Mention the API gateway, correlation IDs, and how every service follows the same internal patterns (structured logging, health endpoints, Alembic migrations, OpenAPI specs). This shows consistency and operational maturity.

**"Why microservices for a portfolio project?"**
Because the enterprise context demands it. Token metering needs to enforce budget limits without blocking the RAG engine. Audit logging must be append-only and decoupled from the services it monitors. Fraud detection and compliance checking serve different teams with different access requirements. The MCP layer enforces tool access boundaries between the agent and the services it calls. Monoliths cannot enforce these boundaries. The trade-off is operational complexity, which Docker Compose and the Makefile absorb for development.

**"How does the agentic investigation work?"**
The Claude Agent SDK runs an autonomous loop. It receives a fraud alert, then plans and executes tool calls: `fraud_get_alert` for transaction context, `rag_retrieve` for relevant SOPs, `fraud_similar_cases` for pattern matching. Before presenting to the analyst, it runs an evaluator-optimizer step, checking its own summary against a rubric and re-running if confidence is below threshold. For escalated cases it spawns a subagent for deeper document retrieval. All tool calls are logged before execution, and the agent cannot approve its own resolution.

**"How do you handle data privacy?"**
PII detection runs before any LLM call using Microsoft Presidio. Masked fields are logged (the fact that masking occurred, not the original values). The audit service records what data was sent to which model, by whom, for which use case, including every agent tool call. RBAC ensures only authorized roles can access investigation data. MCP tool schemas enforce minimal surface area: the agent cannot read fields it does not need. Budget limits prevent any single team from making unlimited LLM calls.

**"What would you change for true production?"**
Replace Docker Compose with Kubernetes. Add a service mesh (Istio) for mTLS between services. Move from Redis pub/sub to Kafka for durable event streaming. Add a model registry (MLflow) for fraud model versioning. Implement blue/green deployments for zero-downtime model updates. Add end-to-end encryption for data at rest. Move MCP servers to SSE transport for production scalability. These are documented in the ADRs as "future state" decisions.

---

## GitHub Topics / Tags

```
enterprise-ai, rag, vector-database, fraud-detection, compliance, llm-governance,
microservices, fastapi, qdrant, xgboost, data-privacy, rbac, pii-masking,
token-metering, audit-logging, python, react, docker, langchain, mlops,
claude-agent-sdk, model-context-protocol, mcp, agentic-ai, prompt-engineering
```
