"""Domain enumerations for the Indian Stock Research & Prediction Platform.

These enums encode the bounded vocabulary of the domain and are referenced by
domain models, ports, and adapters alike. They carry ZERO external dependencies
— only Python stdlib + enum.
"""

from enum import Enum


# ─────────────────────────────────────────────────────────────────────────────
# Market & Exchange
# ─────────────────────────────────────────────────────────────────────────────

class Exchange(str, Enum):
    """Indian stock exchanges supported by the platform."""
    NSE = "NSE"
    BSE = "BSE"


# ─────────────────────────────────────────────────────────────────────────────
# Financial Statement Types
# ─────────────────────────────────────────────────────────────────────────────

class StatementType(str, Enum):
    """Types of financial statements the platform can retrieve."""
    INCOME_STATEMENT = "income_statement"
    BALANCE_SHEET = "balance_sheet"
    CASH_FLOW = "cash_flow"


class PeriodType(str, Enum):
    """Reporting period granularity."""
    ANNUAL = "annual"
    QUARTERLY = "quarterly"


# ─────────────────────────────────────────────────────────────────────────────
# Valuation Scenarios
# ─────────────────────────────────────────────────────────────────────────────

class ScenarioType(str, Enum):
    """Scenario labels for valuation forecasting (Bull / Base / Bear)."""
    BULL = "bull"
    BASE = "base"
    BEAR = "bear"


# ─────────────────────────────────────────────────────────────────────────────
# Recommendation & Risk
# ─────────────────────────────────────────────────────────────────────────────

class RecommendationAction(str, Enum):
    """Final actionable recommendation for a stock."""
    STRONG_BUY = "strong_buy"
    BUY = "buy"
    HOLD = "hold"
    SELL = "sell"
    STRONG_SELL = "strong_sell"


class RiskLevel(str, Enum):
    """Risk classification for an investment thesis."""
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    VERY_HIGH = "very_high"


# ─────────────────────────────────────────────────────────────────────────────
# Screener Filter Operators
# ─────────────────────────────────────────────────────────────────────────────

class FilterOperator(str, Enum):
    """Comparison operators used in multi-factor screener filters."""
    GT = "gt"           # greater than
    GTE = "gte"         # greater than or equal
    LT = "lt"           # less than
    LTE = "lte"         # less than or equal
    EQ = "eq"           # equal
    BETWEEN = "between" # range (requires two values)
