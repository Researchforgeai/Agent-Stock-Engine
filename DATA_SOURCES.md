# Data Sources Architecture & Sourcing Plan

This document defines all **Data Sources**, their exact operational purpose, target Outbound Ports, and the concrete Adapters responsible for fetching and normalizing data for the Indian Stock Research & Prediction Platform.

---

## 1. Architectural Strategy

Following **Hexagonal Architecture (Ports & Adapters)**, the Application Core has zero knowledge of where data originates. Data sources are plugged in via abstract **Outbound Ports**.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            APPLICATION CORE                                 │
│  (Domain Models: StockQuote, FinancialStatement, ScreenerResult, etc.)     │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ Abstract Interfaces
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                            OUTBOUND PORTS                                   │
│  (`MarketDataPort`, `FinancialDataPort`, `ScreenerPort`, `TranscriptPort`)   │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ Implemented by Adapters
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                     SECONDARY DATA ADAPTERS & SOURCES                       │
│                                                                             │
│  ┌─────────────────────────┐  ┌─────────────────────────┐  ┌──────────────┐ │
│  │   adapters/outbound/    │  │   adapters/outbound/    │  │  adapters/   │ │
│  │   data/market_data.py   │  │   data/financials.py    │  │  screener.py │ │
│  └────────────┬────────────┘  └────────────┬────────────┘  └──────┬───────┘ │
│               │                            │                      │         │
└───────────────┼────────────────────────────┼──────────────────────┼─────────┘
                │                            │                      │
                ▼                            ▼                      ▼
┌──────────────────────────────┬──────────────────────────┬───────────────────┐
│     Yahoo Finance API        │  Financial Computation   │   Screener.in /   │
│   (`yfinance` - NSE/BSE)     │   Engine (Ind-AS/GAAP)   │  Rule Screener    │
└──────────────────────────────┴──────────────────────────┴───────────────────┘
```

---

## 2. Planned Data Sources Matrix

| # | Data Source | Technology / Provider | Purpose & Data Provided | Target Port | Adapter File | Phase | Cost |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **1** | **Yahoo Finance** | `yfinance` Python SDK | **Market Data & Prices:** Live/near-real-time quotes, 52W High/Low, day change, trading volume, historical 5Y/10Y OHLCV series, trailing P/E, P/B, Market Cap. | `MarketDataPort` | `adapters/outbound/data/market_data.py` | MVP (Phase 1) | **Free** |
| **2** | **Financial Statements** | `yfinance` + Direct Parser | **Financial Statements:** Normalised annual and quarterly Income Statements (P&L), Balance Sheets, and Cash Flow Statements. | `FinancialDataPort` | `adapters/outbound/data/financials.py` | MVP (Phase 1) | **Free** |
| **3** | **Financial Ratios Engine** | Internal Derived Engine | **Computed Key Ratios:** Indian fundamental health metrics — ROCE (EBIT / Capital Employed), ROE, Debt-to-Equity, Interest Coverage Ratio, Operating Margin, Net Margin, YoY Revenue & Profit growth. | `FinancialDataPort` | `adapters/outbound/data/financials.py` | MVP (Phase 1) | **Internal** |
| **4** | **Stock Screener** | Screener.in / Filter Engine | **Multi-Factor Stock Discovery:** Quantitative filtering of ~2,000+ Indian listed equities by ROCE > 20%, D/E < 0.5, Market Cap thresholds, and growth filters. Powers the Weekend Top 5 discovery pipeline. | `ScreenerPort` | `adapters/outbound/data/screener.py` | MVP (Phase 1) | **Free / Internal** |
| **5** | **Concall Transcripts** | Public Filings / Concall APIs | **Management Guidance & Transcripts:** Quarter earnings call transcripts, CEO/CFO outlook, CapEx plans, margin guidance, and analyst Q&A exchanges. | `TranscriptPort` | `adapters/outbound/data/transcripts.py` | MVP (Phase 1) | **Free / Public** |
| **6** | **Exchange Disclosures & News** | Tavily API / Google News | **Qualitative News & Governance Signals:** SEBI filings, corporate action announcements, promoter share pledging changes, auditor comments, and major news. | `MarketDataPort` / Search | `adapters/outbound/data/news_search.py` | Phase 2 | **Free tier** |
| **7** | **Official Exchange Feeds** | NSE India API (`nsepython`) | **Official Exchange Metrics:** Official shareholding patterns, FII/DII net flows, delivery percentage, and board meeting outcomes. | `MarketDataPort` | `adapters/outbound/data/nse_official.py` | Phase 2 | **Free** |

---

## 3. Deep-Dive: What Data Each Source Provides & Why

### 3.1. Yahoo Finance (`yfinance`) — Primary Price & Multiple Sourcing
- **Ticker Format:** Appends `.NS` for National Stock Exchange (e.g., `RELIANCE.NS`, `TCS.NS`, `HDFCBANK.NS`) and `.BO` for Bombay Stock Exchange (`RELIANCE.BO`).
- **What it provides:**
  - Real-time/near-real-time price snapshots (`currentPrice`, `dayHigh`, `dayLow`, `fiftyTwoWeekHigh`, `fiftyTwoWeekLow`, `volume`).
  - Historical OHLCV candle series over custom windows (1D, 5D, 1M, 1Y, 5Y, Max).
  - Multiples: Trailing P/E, Forward P/E, Price-to-Book (P/B), Dividend Yield.
- **Why used:** Zero cost, highly reliable, no API key setup needed, covers all NSE/BSE equities out of the box.

### 3.2. Financial Statements & Derived Ratios Engine — Fundamental Audit
- **What it provides:**
  - **P&L (Income Statement):** Total Revenue, Cost of Revenue, Gross Profit, Operating Expenses, EBITDA, EBIT, Interest Expense, Tax, Net Profit, EPS.
  - **Balance Sheet:** Total Assets, Cash & Cash Equivalents, Inventories, Accounts Receivable, Total Debt, Long-Term Debt, Current Debt, Shareholder Equity, Capital Employed.
  - **Cash Flow:** Operating Cash Flow (OCF), Capital Expenditure (CapEx), Free Cash Flow (FCF), Financing & Investing Cash Flows.
  - **Computed Ratios:**
    $$\text{ROCE} = \frac{\text{EBIT}}{\text{Total Assets} - \text{Current Liabilities}}$$
    $$\text{ROE} = \frac{\text{Net Income}}{\text{Shareholders' Equity}}$$
    $$\text{Debt-to-Equity} = \frac{\text{Total Debt}}{\text{Shareholders' Equity}}$$
    $$\text{Interest Coverage} = \frac{\text{EBIT}}{\text{Interest Expense}}$$
- **Why used:** Raw financial statements alone aren't enough for equity research; calculating standardized ratios lets specialist agents run health audits and red-flag checks.

### 3.3. Screener Engine — Weekend Discovery Pipeline
- **What it provides:**
  - Multi-factor quantitative filtering across the Indian market universe.
  - Filters include: Market Cap threshold (e.g. $> 1,000$ Cr), ROCE $> 15\%$, Debt-to-Equity $< 0.5$, 3-year Sales Growth $> 10\%$.
- **Why used:** Required for MVP Capability #1 (Automated Weekend Top 5 Recommendation Pipeline).

### 3.4. Earnings Call Transcripts — Management Commentary
- **What it provides:**
  - Verbatim transcripts of management commentary and analyst Q&A.
  - Extracted guidance topics: Revenue outlook, CapEx plans, margin guidance, new product pipelines.
- **Why used:** Provides qualitative evidence backing scenario-based price targets (Bull / Base / Bear cases).

---

## 4. Extensibility & Future Data Upgrades

Because all business logic accesses data through abstract **Outbound Ports** (`MarketDataPort`, `FinancialDataPort`, `ScreenerPort`, `TranscriptPort`), future premium data sources can be added seamlessly:

- **Zerodha Kite Connect API / Angel One API:** Live order book and tick-by-tick market data.
- **Bloomberg / TickerTape / Trendlyne APIs:** Institutional-grade data and analyst target consensus.
- **CMIE Prowess IQ:** Comprehensive database for historical Indian corporate financials.
