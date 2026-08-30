# Indian Stock Research & Prediction Platform

An AI-assisted financial intelligence engine designed for evidence-backed fundamental equity research, probabilistic valuation forecasting, and automated stock discovery for Indian equities (NSE & BSE).

---

## 1. Core MVP Capabilities

1. **Weekly Top 5 Stock Recommendations:** Automated weekend batch pipeline that runs multi-factor quantitative screening, executes specialist multi-agent evaluations, and generates a conviction-ranked digest of top 5 investment theses.
2. **On-Demand Stock Analysis & Price Target Predictions:** Interactive lookup providing deep-dive fundamental health audits, governance checks, and scenario-based future price target predictions (Bull / Base / Bear cases) backed by exact filing citations.

> [!NOTE]
> **Decision-Support Only:** The platform does not place automated brokerage orders or manage live portfolios.

---

## 2. Architectural Overview: The 3 Decoupled Tiers

The system follows a strict 3-tier decoupled architecture where every layer has a single responsibility and zero unnecessary dependencies:

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                          TIER 1: `tools/` (Data & MCP)                          │
│  (Data Fetchers, Tool Callables & MCP Endpoints)                                │
│  • financials.py              • market_data.py                                  │
│  • transcripts.py             • screener.py                                     │
│  • mcp_server.py (FastMCP wrapper)                                              │
│  (Pure data fetching & API normalization — 0 knowledge of Agents or DB)         │
└────────────────────────────────────────┬────────────────────────────────────────┘
                                         │ Injected into (as callable tools)
                                         ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                          TIER 2: `agents/` (Reasoning)                          │
│  (LLM Prompt Chains, Specialist Agents & Graph Orchestrator)                    │
│  • prompts.py                 • specialists.py                                  │
│  • orchestrator.py (LangGraph )                                                 │
│  (Pure cognitive reasoning — 0 knowledge of FastAPI routes or DB tables)        │
└────────────────────────────────────────┬────────────────────────────────────────┘
                                         │ Invoked by
                                         ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                          TIER 3: `app/` (Backend Core)                          │
│  (Business Logic, Domain Models & Persistence)                                  │
│  • models/ (Pydantic Domain Schemas & Contracts)                                │
│  • use_cases.py (Business Handlers & Workflow Orchestration)                    │
│  • unit_of_work.py (Transaction Context Manager)                                │
│  • repository.py (Pydantic-to-SQLite/Postgres JSON Store — NO ORM!)             │
│  • notifications.py (Telegram / Email Alerts)                                   │
└────────────────────────────────────────┬────────────────────────────────────────┘
                                         ▲
                                         │ Called by
┌────────────────────────────────────────┴────────────────────────────────────────┐
│                      TIER 4: `entrypoints/` (Drivers)                           │
│  (Inbound HTTP, CLI, and Scheduled Cron triggers)                               │
│  • api.py (FastAPI)           • cli.py (Typer)     • scheduler.py (Cron)        │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Directory & Package Structure

```text
stock_analysis/
│
├── src/
│   └── stock_analysis/
│       │
│       ├── tools/                                # TIER 1: ON-DEMAND DATA TOOLS & MCP
│       │   ├── __init__.py
│       │   ├── base.py                           # Abstract Tool interface
│       │   ├── financials.py                     # Normalized balance sheets, P&L, cash flows, ratios
│       │   ├── market_data.py                    # Live quotes, historical valuation multiples, OHLCV
│       │   ├── transcripts.py                    # Concall transcripts & management guidance search
│       │   ├── screener.py                       # External stock screener API client
│       │   └── mcp_server.py                     # FastMCP registry exposing all tools via MCP protocol
│       │
│       ├── agents/                               # TIER 2: SPECIALIST AGENTS & REASONING
│       │   ├── __init__.py
│       │   ├── prompts.py                        # System prompts & analytical guardrails
│       │   ├── specialists.py                    # FundamentalsAgent, ValuationAgent, GovernanceAgent
│       │   └── orchestrator.py                   # Swappable runner (LangGraph / Google Agent SDK)
│       │
│       ├── app/                                  # TIER 3: BACKEND CORE & PERSISTENCE
│       │   ├── __init__.py
│       │   ├── models/                           # Modular Pydantic domain models
│       │   │   ├── __init__.py                   # Model registry & public exports
│       │   │   ├── enums.py                      # Exchange, RecommendationAction, RiskLevel
│       │   │   ├── inputs.py                     # AnalyzeStockInput, DiscoverStocksInput
│       │   │   ├── technicals.py                 # Technical indicators & trend analysis
│       │   │   ├── fundamentals.py               # Growth, margins, ROCE, debt health
│       │   │   ├── valuation.py                  # Multi-year price matrix & scenario models
│       │   │   ├── thesis.py                     # InvestmentThesis & ThesisAntiThesis
│       │   │   └── discovery.py                  # WeeklyDigest & Multibagger candidate models
│       │   ├── use_cases.py                      # AnalyzeStockUseCase, WeeklyDiscoveryUseCase
│       │   ├── unit_of_work.py                   # Atomic transaction context manager (`with uow:`)
│       │   ├── repository.py                     # Pydantic-to-SQLite/Postgres JSON store (NO ORM!)
│       │   └── notifications.py                  # Outbound Telegram / Email alerts
│       │
│       ├── entrypoints/                          # TIER 4: INBOUND ENTRYPOINTS
│       │   ├── __init__.py
│       │   ├── api.py                            # FastAPI application & REST endpoints
│       │   ├── cli.py                            # Typer interactive terminal CLI
│       │   └── scheduler.py                      # APScheduler cron runner for weekend top 5
│       │
│       ├── bootstrap.py                          # DI Root (Wires tools -> agents -> app)
│       └── config.py                             # Settings, environment variables, API keys
│
├── tests/
│   ├── unit/
│   │   ├── test_tools.py                         # Mock HTTP tests for tool parsers
│   │   ├── test_agents.py                        # Mock tool tests for agent reasoning
│   │   └── test_use_cases.py                     # In-memory FakeUnitOfWork tests
│   └── e2e/
│       └── test_api.py                           # FastAPI TestClient end-to-end tests
│
├── .dockerignore                                 # Build context ignore rules
├── .env.example                                  # Environment variables and API keys template
├── docker-compose.yml                            # Multi-container orchestration (API, Scheduler, DB)
├── Dockerfile                                    # Multi-stage production container build
├── pyproject.toml                                # Dependency specification & build configuration
├── REQUIREMENTS.md                               # Comprehensive system requirements
├── LLD.md                                        # Low-Level Design specification
└── README.md
```

---

## 4. Naming Conventions & Layer Isolation Invariants

| Layer | Responsibility | Isolation Invariant |
| :--- | :--- | :--- |
| **`tools/`** | Fetches live market quotes, filings, concalls, and screener results on demand. | **Zero** knowledge of Agents or Databases. Functions only take parameters and return clean data structures. |
| **`agents/`** | Cognitive LLM reasoning layer (Fundamentals, Valuation, Governance, Synthesis). | **Zero** knowledge of FastAPI routes or database tables. Receives tools via dependency injection. |
| **`app/`** | Coordinates business use cases, manages database transactions, and persists reports. | **Zero** knowledge of prompt engineering or external API wire formats. Uses Unit of Work for storage. |
| **`entrypoints/`** | Inbound triggers (REST API, CLI, Cron). | Ultra-thin adapters. Parses user input, invokes use cases, and serializes JSON responses. |
| **`bootstrap.py`** | Composition Root. | The **only** place in the codebase where concrete tools, agents, and storage adapters are wired together. |

---
