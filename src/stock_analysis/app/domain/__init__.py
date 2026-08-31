"""Domain layer — pure business entities, value objects, and enumerations.

All exports are available directly from ``stock_analysis.app.domain``.
"""

from stock_analysis.app.domain.enums import (
    Exchange,
    FilterOperator,
    PeriodType,
    RecommendationAction,
    RiskLevel,
    ScenarioType,
    StatementType,
)
from stock_analysis.app.domain.models import (
    FinancialLineItem,
    FinancialRatios,
    FinancialStatement,
    FuturePriceMatrix,
    HistoricalPrice,
    HistoricalValuation,
    ScreenerFilter,
    ScreenerResult,
    StockQuote,
    TranscriptSegment,
    ValuationScenario,
)

__all__ = [
    # Enums
    "Exchange",
    "FilterOperator",
    "PeriodType",
    "RecommendationAction",
    "RiskLevel",
    "ScenarioType",
    "StatementType",
    # Models
    "FinancialLineItem",
    "FinancialRatios",
    "FinancialStatement",
    "FuturePriceMatrix",
    "HistoricalPrice",
    "HistoricalValuation",
    "ScreenerFilter",
    "ScreenerResult",
    "StockQuote",
    "TranscriptSegment",
    "ValuationScenario",
]
