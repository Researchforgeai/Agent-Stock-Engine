"""Exchange identifiers used by stock quotes."""

from enum import Enum


class Exchange(str, Enum):
    """Indian stock exchanges supported by the platform."""
    NSE = "NSE"
    BSE = "BSE"
