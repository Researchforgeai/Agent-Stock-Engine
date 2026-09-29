# Indian Stock Research & Prediction Platform

An AI-assisted financial intelligence engine designed for evidence-backed fundamental equity research, probabilistic valuation forecasting, and automated stock discovery for Indian equities (NSE & BSE).

## Implementation Status

The current implementation provides a stock quote tool backed by the saved Reliance
sample and wired into a Google ADK research agent. Sample quotes are historical,
not live market data.

The capabilities, architecture, and directory structure below describe the target
design, not a list of implemented features. Domain types and port methods are added
only when a working feature needs them. Currently, the core contains `Exchange`,
`StockQuote`, and `MarketDataPort.get_quote`; package initializers remain empty.
Price history, financial statements, screening, transcripts, and valuation scenarios
are deferred until their corresponding features are implemented.

---

## 1. Core MVP Capabilities

1. **Weekly Top 5 Stock Recommendations:** Automated weekend batch pipeline that runs multi-factor quantitative screening, executes specialist multi-agent evaluations, and generates a conviction-ranked digest of top 5 investment theses.
2. **On-Demand Stock Analysis & Price Target Predictions:** Interactive lookup providing deep-dive fundamental health audits, governance checks, and scenario-based future price target predictions (Bull / Base / Bear cases) backed by exact filing citations.

> [!NOTE]
> **Decision-Support Only:** The platform does not place automated brokerage orders or manage live portfolios.

---

## 2. Architectural Overview: Hexagonal Architecture (Ports & Adapters)

The system follows a **Hexagonal (Ports & Adapters)** architecture where the Application Core is completely isolated from all external concerns. External systems (HTTP, CLI, databases, market data APIs) interact with the Core exclusively through well-defined Port interfaces.

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                             PRIMARY ADAPTERS (Driving / Inbound)                                     │
│               FastAPI (REST)           Typer (CLI)          APScheduler (Cron)                       │
└──────────────────────────┬───────────────────┬─────────────────────┬────────────────────────────────┘
                           │                   │                     │
                           │  AnalyzeStockCommand / DiscoverStocksCommand (Inbound DTOs)
                           ▼                   ▼                     ▼
┌──────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                        APPLICATION CORE (Inside)                                     │
│                                                                                                      │
│   ┌──────────────────────────────────────────────────────────────────────────────────────────────┐   │
│   │                              APPLICATION LAYER                                               │   │
│   │   commands.py            use_cases.py                                                        │   │
│   │   • AnalyzeStockCommand  • AnalyzeStockUseCase ──────────────────────────────────────────►  │   │
│   │   • DiscoverStocksCommand• WeeklyDiscoveryUseCase                                           │   │
│   └──────────────────────────────────────────────────────────────────────────────────────────────┘   │
│                                             │                                                        │
│                                             ▼                                                        │
│   ┌──────────────────────────────────────────────────────────────────────────────────────────────┐   │
│   │                                DOMAIN CORE                                                   │   │
│   │   domain/                                                                                    │   │
│   │   • InvestmentThesis (Aggregate Root)   • ValuationScenario (Value Object)                   │   │
│   │   • FundamentalsAudit (Value Object)    • TechnicalAudit (Value Object)                      │   │
│   │   • WeeklyDigest (Entity)               • GovernanceAudit (Value Object)                     │   │
│   └──────────────────────────────────────────────────────────────────────────────────────────────┘   │
│                                             │                                                        │
│                                             ▼                                                        │
│   ┌──────────────────────────────────────────────────────────────────────────────────────────────┐   │
│   │                               OUTBOUND PORTS (Abstract Interfaces)                           │   │
│   │   ports/outbound.py                                                                          │   │
│   │   • FinancialDataPort       • MarketDataPort        • TranscriptPort                         │   │
│   │   • ThesisRepositoryPort    • NotificationPort      • ScreenerPort                           │   │
│   └──────────────────────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                                      │
└──────────────────────────────────────────────────────────────────────────────────────────────────────┘
                           │                   │                     │
                           │  Implemented by Secondary / Driven Adapters
                           ▼                   ▼                     ▼
┌──────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                             SECONDARY ADAPTERS (Driven / Outbound)                                   │
│       yfinance / Screener.in / Concall APIs       SQLite / Postgres       Telegram / Email           │
└──────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Directory & Package Structure

```text
stock_analysis/
│
├── src/
│   └── stock_analysis/
│       │
│       ├── app/                                          # APPLICATION CORE (Inside)
│       │   ├── __init__.py
│       │   │
│       │   ├── commands.py                               # Inbound DTOs (AnalyzeStockCommand, DiscoverStocksCommand)
│       │   ├── use_cases.py                              # Application orchestration (AnalyzeStockUseCase, WeeklyDiscoveryUseCase)
│       │   │
│       │   ├── domain/                                   # DOMAIN CORE: Entities & Value Objects
│       │   │   ├── __init__.py
│       │   │   ├── enums.py                              # Exchange, RecommendationAction, RiskLevel, ScenarioType
│       │   │   ├── analysis.py                           # InvestmentThesis, FundamentalsAudit, TechnicalAudit, GovernanceAudit
│       │   │   ├── valuation.py                          # ValuationScenario, FuturePriceMatrix (Bull / Base / Bear)
│       │   │   └── discovery.py                          # WeeklyDigest, MultibaggerPick
│       │   │
│       │   └── ports/                                    # DEPENDENCY BOUNDARIES (Abstract Interfaces)
│       │       ├── __init__.py
│       │       └── outbound.py                           # FinancialDataPort, MarketDataPort, ThesisRepositoryPort, NotificationPort
│       │
│       ├── adapters/                                     # CONCRETE ADAPTERS (Outside)
│       │   ├── __init__.py
│       │   │
│       │   ├── inbound/                                  # PRIMARY ADAPTERS (Driving)
│       │   │   ├── __init__.py
│       │   │   ├── api.py                                # FastAPI REST adapter
│       │   │   ├── cli.py                                # Typer interactive terminal CLI adapter
│       │   │   └── scheduler.py                          # APScheduler cron adapter for weekend top 5
│       │   │
│       │   └── outbound/                                 # SECONDARY ADAPTERS (Driven)
│       │       ├── __init__.py
│       │       ├── data/                                 # Market & Financial data fetchers (implements Outbound Ports)
│       │       │   ├── __init__.py
│       │       │   ├── financials.py                     # Normalized balance sheets, P&L, cash flows, ratios
│       │       │   ├── market_data.py                    # Live quotes, historical valuation multiples, OHLCV
│       │       │   ├── screener.py                       # External stock screener API client
│       │       │   ├── transcripts.py                    # Concall transcripts & management guidance search
│       │       │   └── mcp_server.py                     # FastMCP registry exposing all data adapters via MCP protocol
│       │       ├── tools/                                # LLM-CALLABLE TOOL WRAPPERS (independent of any specific agent)
│       │       │   ├── __init__.py
│       │       │   ├── financials_tool.py                # Wraps financials data adapter as LLM-callable tool schema
│       │       │   ├── market_data_tool.py               # Wraps market data adapter as LLM-callable tool schema
│       │       │   ├── screener_tool.py                  # Wraps screener adapter as LLM-callable tool schema
│       │       │   └── transcripts_tool.py               # Wraps transcripts adapter as LLM-callable tool schema
│       │       ├── repository.py                         # Implements ThesisRepositoryPort (Pydantic-to-SQLite/Postgres, NO ORM)
│       │       └── notifications.py                      # Implements NotificationPort (Telegram / Email alerts)
│       │
│       ├── agents/                                       # AI REASONING LAYER (Pure Reasoning — No I/O)
│       │   ├── __init__.py
│       │   ├── prompts.py                                # System prompts & analytical guardrails
│       │   ├── specialists.py                            # FundamentalsAgent, ValuationAgent, GovernanceAgent
│       │   └── orchestrator.py                           # Swappable runner (LangGraph / Google Agent SDK)
│       │
│       ├── bootstrap.py                                  # Composition Root — wires adapters to ports & injects into use cases
│       └── config.py                                     # Settings, environment variables, API keys
│
├── tests/
│   ├── unit/
│   │   ├── test_domain.py                                # Domain entity & value object tests
│   │   ├── test_use_cases.py                             # In-memory FakeRepository use case tests
│   │   └── test_agents.py                                # Mock tool tests for agent reasoning
│   └── e2e/
│       └── test_api.py                                   # FastAPI TestClient end-to-end tests
│
├── .dockerignore                                         # Build context ignore rules
├── .env.example                                          # Environment variables and API keys template
├── docker-compose.yml                                    # Multi-container orchestration (API, Scheduler, DB)
├── Dockerfile                                            # Multi-stage production container build
├── pyproject.toml                                        # Dependency specification & build configuration
├── REQUIREMENTS.md                                       # Comprehensive system requirements
├── LLD.md                                                # Low-Level Design specification
└── README.md
```

---

## 4. Layer Responsibilities & Isolation Invariants

| Layer | Responsibility | Isolation Invariant |
| :--- | :--- | :--- |
| **`adapters/inbound/`** | Primary Adapters — parse raw HTTP requests, CLI args, and cron triggers into Commands. | **Zero** domain logic. Constructs Commands and delegates entirely to Use Cases. |
| **`app/commands.py`** | Inbound DTOs representing user intent (Commands). | **Zero** knowledge of HTTP, CLI, or DB. Pure Python dataclasses / Pydantic models. |
| **`app/use_cases.py`** | Application orchestration — coordinates agents, ports, and domain assembly. | **Zero** knowledge of HTTP routes, DB wire formats, or external API structures. |
| **`app/domain/`** | Domain Core — pure business entities and value objects encoding the investment thesis logic. | **Zero** knowledge of FastAPI, databases, or external APIs. No I/O of any kind. |
| **`app/ports/outbound.py`** | Abstract Port interfaces defining what the Application Core needs from the outside world. | **Zero** knowledge of concrete implementations. Pure Python `Protocol` or `ABC` definitions. |
| **`adapters/outbound/`** | Secondary Adapters — concrete implementations of Outbound Ports (market data APIs, DB, notifications). | **Zero** domain logic. Purely maps external data to the contracts defined by Outbound Ports. |
| **`adapters/outbound/tools/`** | LLM-Callable Tool Wrappers — adapts raw outbound data fetchers into structured, schema-validated tool definitions consumable by any LLM agent or orchestrator. Independent of any specific agent. | **Zero** domain logic or agent-specific reasoning. Purely defines the callable interface (name, description, args schema) and delegates to the corresponding data adapter. |
| **`agents/`** | AI Reasoning Layer — specialist LLM agents invoked by Use Cases to produce domain value objects. Consumes tools from `adapters/outbound/tools/` via dependency injection. | **Zero** knowledge of FastAPI routes, DB tables, or external API wire formats. Pure reasoning and prompt logic only. |
| **`bootstrap.py`** | Composition Root. | The **only** place where concrete adapters are instantiated and wired to ports, tools, and use cases. |

---
