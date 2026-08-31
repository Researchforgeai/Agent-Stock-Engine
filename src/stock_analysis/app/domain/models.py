"""Domain models (Value Objects & Entities) for market data, financial statements,
screener results, and transcript segments.

Design rules:
  • Every model is an immutable Pydantic BaseModel (frozen=True for Value Objects).
  • Models carry ZERO knowledge of HTTP, databases, yfinance, or any adapter.
  • They are the universal data shapes flowing through Ports and Use Cases.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from stock_analysis.app.domain.enums import (
    Exchange,
    FilterOperator,
    PeriodType,
    RecommendationAction,
    RiskLevel,
    ScenarioType,
    StatementType,
)


# ═════════════════════════════════════════════════════════════════════════════
#  MARKET DATA MODELS
# ═════════════════════════════════════════════════════════════════════════════


class StockQuote(BaseModel, frozen=True):
    """Real-time (or near-real-time) price snapshot for a single equity.

    This is the canonical representation returned by ``MarketDataPort.get_quote``.
    """
    symbol: str = Field(..., description="Ticker symbol, e.g. 'RELIANCE'")
    exchange: Exchange = Field(default=Exchange.NSE)
    company_name: str = Field(default="", description="Full registered company name")

    # Price fields
    current_price: float = Field(..., description="Last traded price in INR")
    previous_close: float = Field(default=0.0)
    open_price: float = Field(default=0.0)
    day_high: float = Field(default=0.0)
    day_low: float = Field(default=0.0)

    # 52-week range
    week_52_high: float = Field(default=0.0, description="52-week high price")
    week_52_low: float = Field(default=0.0, description="52-week low price")

    # Volume & market cap
    volume: int = Field(default=0, description="Trading volume for the current session")
    market_cap: Optional[float] = Field(default=None, description="Market capitalisation in INR")

    # Key multiples (snapshot)
    pe_ratio: Optional[float] = Field(default=None, description="Trailing P/E ratio")
    pb_ratio: Optional[float] = Field(default=None, description="Price-to-Book ratio")
    dividend_yield: Optional[float] = Field(default=None, description="Trailing dividend yield (%)")

    # Metadata
    timestamp: Optional[datetime] = Field(default=None, description="Quote fetch timestamp (UTC)")


class HistoricalPrice(BaseModel, frozen=True):
    """A single OHLCV data point for historical price series."""
    date: date
    open: float
    high: float
    low: float
    close: float
    volume: int = 0


class HistoricalValuation(BaseModel, frozen=True):
    """Historical valuation multiples (P/E, P/B, EV/EBITDA) computed over a
    look-back window, including percentile bands.
    """
    symbol: str
    period_years: int = Field(default=5, description="Look-back window in years")

    # Trailing P/E band
    pe_median: Optional[float] = None
    pe_current: Optional[float] = None
    pe_percentile_25: Optional[float] = None
    pe_percentile_75: Optional[float] = None

    # Price-to-Book band
    pb_median: Optional[float] = None
    pb_current: Optional[float] = None
    pb_percentile_25: Optional[float] = None
    pb_percentile_75: Optional[float] = None

    # EV/EBITDA band
    ev_ebitda_median: Optional[float] = None
    ev_ebitda_current: Optional[float] = None


# ═════════════════════════════════════════════════════════════════════════════
#  FINANCIAL STATEMENT MODELS
# ═════════════════════════════════════════════════════════════════════════════


class FinancialLineItem(BaseModel, frozen=True):
    """A single row in a financial statement (e.g. "Revenue" = ₹2,35,000 Cr)."""
    label: str = Field(..., description="Line item name, e.g. 'Total Revenue'")
    value: Optional[float] = Field(default=None, description="Value in INR (raw, not in Cr)")
    period_end: date = Field(..., description="Reporting period end date")
    period_type: PeriodType = Field(default=PeriodType.ANNUAL)


class FinancialStatement(BaseModel, frozen=True):
    """A complete financial statement for a given ticker and period.

    Contains a list of normalised line items (Revenue, EBITDA, Net Profit,
    Total Assets, etc.) for a single reporting period.
    """
    symbol: str
    statement_type: StatementType
    period_type: PeriodType
    period_end: date
    currency: str = Field(default="INR")
    line_items: List[FinancialLineItem] = Field(default_factory=list)

    def get_item(self, label: str) -> Optional[FinancialLineItem]:
        """Lookup a line item by its label (case-insensitive)."""
        label_lower = label.lower()
        for item in self.line_items:
            if item.label.lower() == label_lower:
                return item
        return None


class FinancialRatios(BaseModel, frozen=True):
    """Computed financial ratios derived from statements.

    These are the key metrics an analyst uses for fundamental health audits.
    """
    symbol: str
    period_end: date
    period_type: PeriodType = Field(default=PeriodType.ANNUAL)

    # Profitability
    roe: Optional[float] = Field(default=None, description="Return on Equity (%)")
    roce: Optional[float] = Field(default=None, description="Return on Capital Employed (%)")
    operating_margin: Optional[float] = Field(default=None, description="Operating Margin (%)")
    net_margin: Optional[float] = Field(default=None, description="Net Profit Margin (%)")
    ebitda_margin: Optional[float] = Field(default=None, description="EBITDA Margin (%)")

    # Solvency
    debt_to_equity: Optional[float] = Field(default=None, description="Total Debt / Total Equity")
    current_ratio: Optional[float] = Field(default=None, description="Current Assets / Current Liabilities")
    interest_coverage: Optional[float] = Field(default=None, description="EBIT / Interest Expense")

    # Efficiency
    asset_turnover: Optional[float] = Field(default=None, description="Revenue / Total Assets")
    inventory_turnover: Optional[float] = Field(default=None, description="COGS / Average Inventory")

    # Growth (YoY)
    revenue_growth_yoy: Optional[float] = Field(default=None, description="Revenue growth YoY (%)")
    profit_growth_yoy: Optional[float] = Field(default=None, description="Net profit growth YoY (%)")
    eps_growth_yoy: Optional[float] = Field(default=None, description="EPS growth YoY (%)")


# ═════════════════════════════════════════════════════════════════════════════
#  SCREENER MODELS
# ═════════════════════════════════════════════════════════════════════════════


class ScreenerFilter(BaseModel, frozen=True):
    """A single filter criterion for multi-factor stock screening.

    Example: ``ScreenerFilter(field="market_cap", operator=FilterOperator.GT, value=10_000_000_000)``
    means "Market Cap > ₹10,000 Cr".
    """
    field: str = Field(..., description="The metric to filter on, e.g. 'market_cap', 'roce', 'debt_to_equity'")
    operator: FilterOperator = Field(default=FilterOperator.GTE)
    value: float = Field(..., description="Primary threshold value")
    value_upper: Optional[float] = Field(default=None, description="Upper bound for BETWEEN operator")


class ScreenerResult(BaseModel, frozen=True):
    """A single stock row returned by the screener."""
    symbol: str
    company_name: str = ""
    exchange: Exchange = Field(default=Exchange.NSE)
    current_price: Optional[float] = None
    market_cap: Optional[float] = None

    # The metric values that matched the filters
    matched_metrics: Dict[str, float] = Field(
        default_factory=dict,
        description="Key-value map of metric names to their values, e.g. {'roce': 22.5, 'debt_to_equity': 0.3}",
    )


# ═════════════════════════════════════════════════════════════════════════════
#  TRANSCRIPT MODELS
# ═════════════════════════════════════════════════════════════════════════════


class TranscriptSegment(BaseModel, frozen=True):
    """A semantically meaningful segment from an earnings call transcript.

    Could be a management commentary paragraph, an analyst Q&A exchange,
    or a forward-looking guidance statement.
    """
    symbol: str
    quarter: str = Field(..., description="Reporting quarter, e.g. 'Q3 FY2025'")
    speaker: str = Field(default="Unknown", description="Name of the speaker")
    role: str = Field(default="", description="Speaker's role, e.g. 'CEO', 'CFO', 'Analyst'")
    text: str = Field(..., description="Transcript text content")
    segment_type: str = Field(
        default="commentary",
        description="Type of segment: 'commentary', 'guidance', 'qa'",
    )
    topics: List[str] = Field(
        default_factory=list,
        description="Extracted topic tags, e.g. ['revenue_outlook', 'capex', 'margin_guidance']",
    )
    source_url: Optional[str] = Field(default=None, description="URL of the original transcript source")


# ═════════════════════════════════════════════════════════════════════════════
#  VALUATION SCENARIO MODELS 
# ═════════════════════════════════════════════════════════════════════════════


class ValuationScenario(BaseModel, frozen=True):
    """A single scenario (Bull / Base / Bear) price target with assumptions."""
    scenario_type: ScenarioType
    target_price: float = Field(..., description="Predicted price in INR")
    upside_pct: float = Field(default=0.0, description="Upside/downside from current price (%)")
    probability: float = Field(default=0.0, ge=0, le=1, description="Assigned probability (0-1)")
    time_horizon_months: int = Field(default=12, description="Forecast horizon in months")
    key_assumptions: List[str] = Field(
        default_factory=list,
        description="Assumptions underpinning this scenario",
    )
    methodology: str = Field(default="", description="Valuation methodology used, e.g. 'DCF', 'Relative Valuation'")


class FuturePriceMatrix(BaseModel, frozen=True):
    """Aggregated price target matrix containing all three scenarios."""
    symbol: str
    current_price: float
    scenarios: List[ValuationScenario] = Field(default_factory=list)
    weighted_target: Optional[float] = Field(
        default=None,
        description="Probability-weighted blended target price",
    )
    recommendation: Optional[RecommendationAction] = None
    risk_level: Optional[RiskLevel] = None
