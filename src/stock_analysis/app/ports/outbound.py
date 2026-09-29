"""Market data contract required by the stock quote tool."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from stock_analysis.app.domain.enums import Exchange
from stock_analysis.app.domain.models import StockQuote


@runtime_checkable
class MarketDataPort(Protocol):
    """Port for retrieving stock quote snapshots for Indian equities."""

    async def get_quote(self, symbol: str, exchange: Exchange = Exchange.NSE) -> StockQuote:
        """Fetch an available price snapshot for a given ticker.

        Args:
            symbol: NSE/BSE ticker symbol (e.g. ``"RELIANCE"``).
            exchange: Target exchange (defaults to NSE).

        Returns:
            A fully populated ``StockQuote`` value object.
        """
        ...
