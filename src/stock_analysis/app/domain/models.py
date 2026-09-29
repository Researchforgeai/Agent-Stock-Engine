"""Stock quote data shared by the market adapter and quote tool."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from stock_analysis.app.domain.enums import Exchange


class StockQuote(BaseModel, frozen=True):
    """Price snapshot for a single equity, including historical samples.

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
