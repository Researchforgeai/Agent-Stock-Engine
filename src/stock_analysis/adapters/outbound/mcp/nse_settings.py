"""Configuration for NSE's hosted MCP endpoints."""

from __future__ import annotations

import os
from dataclasses import dataclass
from urllib.parse import urlsplit


@dataclass(frozen=True)
class NseMcpSettings:
    bhavcopy_url: str = "https://mcp.nseindia.in/bhavcopy/cm/mcp"
    cm_market_url: str = "https://mcp.nseindia.in/cmmkt/mcp"

    def __post_init__(self) -> None:
        for field_name, url in (
            ("bhavcopy_url", self.bhavcopy_url),
            ("cm_market_url", self.cm_market_url),
        ):
            parsed = urlsplit(url)
            if (
                parsed.scheme != "https"
                or parsed.hostname != "mcp.nseindia.in"
                or parsed.username is not None
                or parsed.password is not None
            ):
                raise ValueError(
                    f"{field_name} must be an HTTPS URL on mcp.nseindia.in"
                )

    @classmethod
    def from_env(cls) -> NseMcpSettings:
        return cls(
            bhavcopy_url=os.getenv(
                "NSE_BHAVCOPY_MCP_URL",
                "https://mcp.nseindia.in/bhavcopy/cm/mcp",
            ),
            cm_market_url=os.getenv(
                "NSE_CM_MARKET_MCP_URL",
                "https://mcp.nseindia.in/cmmkt/mcp",
            ),
        )
