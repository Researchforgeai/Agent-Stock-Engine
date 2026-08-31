"""Outbound Port interfaces (Abstract Contracts) for the Application Core.

These are the **wall sockets** of the hexagonal architecture. They define what
the Application Core *needs* from the outside world, without knowing or caring
*how* those needs are fulfilled.

Design rules:
  • Every port is a ``typing.Protocol`` — structural subtyping, no inheritance required.
  • ZERO external imports (no yfinance, no httpx, no database drivers).
  • Only reference domain models from ``stock_analysis.app.domain.models``.
  • Concrete adapters in ``adapters/outbound/`` implement these protocols.
"""

from __future__ import annotations

from datetime import date
from typing import List, Optional, Protocol, runtime_checkable

from stock_analysis.app.domain.enums import Exchange, PeriodType, StatementType
from stock_analysis.app.domain.models import (
    FinancialRatios,
    FinancialStatement,
    HistoricalPrice,
    HistoricalValuation,
    ScreenerFilter,
    ScreenerResult,
    StockQuote,
    TranscriptSegment,
)


# ═════════════════════════════════════════════════════════════════════════════
#  MARKET DATA PORT
# ═════════════════════════════════════════════════════════════════════════════


@runtime_checkable
class MarketDataPort(Protocol):
    """Port for retrieving real-time quotes, historical prices, and
    historical valuation multiples for Indian equities.
    """

    async def get_quote(self, symbol: str, exchange: Exchange = Exchange.NSE) -> StockQuote:
        """Fetch the latest price snapshot for a given ticker.

        Args:
            symbol: NSE/BSE ticker symbol (e.g. ``"RELIANCE"``).
            exchange: Target exchange (defaults to NSE).

        Returns:
            A fully populated ``StockQuote`` value object.
        """
        ...

    async def get_historical_prices(
        self,
        symbol: str,
        start_date: date,
        end_date: date,
        exchange: Exchange = Exchange.NSE,
    ) -> List[HistoricalPrice]:
        """Fetch OHLCV price history for a given date range.

        Args:
            symbol: NSE/BSE ticker symbol.
            start_date: Start of the date range (inclusive).
            end_date: End of the date range (inclusive).
            exchange: Target exchange.

        Returns:
            Chronologically ordered list of ``HistoricalPrice`` data points.
        """
        ...

    async def get_historical_valuation(
        self,
        symbol: str,
        period_years: int = 5,
        exchange: Exchange = Exchange.NSE,
    ) -> HistoricalValuation:
        """Compute historical valuation percentile bands (P/E, P/B, EV/EBITDA).

        Args:
            symbol: NSE/BSE ticker symbol.
            period_years: Look-back window (e.g. 3, 5, 10 years).
            exchange: Target exchange.

        Returns:
            A ``HistoricalValuation`` value object with median and percentile bands.
        """
        ...


# ═════════════════════════════════════════════════════════════════════════════
#  FINANCIAL DATA PORT
# ═════════════════════════════════════════════════════════════════════════════


@runtime_checkable
class FinancialDataPort(Protocol):
    """Port for retrieving normalised financial statements and computed
    financial ratios.
    """

    async def get_financial_statement(
        self,
        symbol: str,
        statement_type: StatementType = StatementType.INCOME_STATEMENT,
        period_type: PeriodType = PeriodType.ANNUAL,
        exchange: Exchange = Exchange.NSE,
    ) -> List[FinancialStatement]:
        """Retrieve financial statements for a given ticker.

        Args:
            symbol: NSE/BSE ticker symbol.
            statement_type: Income statement, balance sheet, or cash flow.
            period_type: Annual or quarterly reporting.
            exchange: Target exchange.

        Returns:
            A list of ``FinancialStatement`` objects, one per reporting period,
            ordered from most recent to oldest.
        """
        ...

    async def get_financial_ratios(
        self,
        symbol: str,
        period_type: PeriodType = PeriodType.ANNUAL,
        exchange: Exchange = Exchange.NSE,
    ) -> List[FinancialRatios]:
        """Compute and return key financial ratios (ROE, ROCE, D/E, margins).

        Args:
            symbol: NSE/BSE ticker symbol.
            period_type: Annual or quarterly.
            exchange: Target exchange.

        Returns:
            A list of ``FinancialRatios`` objects, one per reporting period,
            ordered from most recent to oldest.
        """
        ...


# ═════════════════════════════════════════════════════════════════════════════
#  SCREENER PORT
# ═════════════════════════════════════════════════════════════════════════════


@runtime_checkable
class ScreenerPort(Protocol):
    """Port for multi-factor quantitative stock screening."""

    async def screen_stocks(
        self,
        filters: List[ScreenerFilter],
        exchange: Exchange = Exchange.NSE,
        limit: int = 50,
    ) -> List[ScreenerResult]:
        """Execute a multi-factor screen against Indian equities.

        Args:
            filters: List of ``ScreenerFilter`` criteria to apply.
            exchange: Restrict to a specific exchange (or both).
            limit: Maximum number of results to return.

        Returns:
            A list of ``ScreenerResult`` objects matching all filter criteria,
            ordered by relevance or market cap descending.
        """
        ...


# ═════════════════════════════════════════════════════════════════════════════
#  TRANSCRIPT PORT
# ═════════════════════════════════════════════════════════════════════════════


@runtime_checkable
class TranscriptPort(Protocol):
    """Port for searching and retrieving earnings call transcript segments."""

    async def search_transcripts(
        self,
        symbol: str,
        query: Optional[str] = None,
        quarter: Optional[str] = None,
        limit: int = 10,
    ) -> List[TranscriptSegment]:
        """Search earnings call transcripts for a given stock.

        Args:
            symbol: NSE/BSE ticker symbol.
            query: Free-text search query (e.g. ``"capex guidance"``).
                   If None, returns the most recent transcript segments.
            quarter: Filter to a specific quarter (e.g. ``"Q3 FY2025"``).
            limit: Maximum number of segments to return.

        Returns:
            A list of ``TranscriptSegment`` objects matching the search criteria.
        """
        ...
