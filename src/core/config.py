"""Core configuration and settings for Agent Stock Engine."""
from typing import List, Optional
from pydantic import Field, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

    # API Settings
    APP_NAME: str = "Agent Stock Engine"
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Agent Stock Engine"
    DEBUG: bool = False
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000", "*"]

    # Database Settings (PostgreSQL + pgvector)
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "stock_engine_db"
    
    # Computed Database URLs
    @property
    def sync_database_url(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    @property
    def async_database_url(self) -> str:
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    # LLM Settings
    DEFAULT_LLM_PROVIDER: str = "google"  # google | openai | anthropic
    
    # Gemini
    GEMINI_API_KEY: Optional[str] = Field(default=None, description="Google Gemini API Key")
    PRIMARY_MODEL: str = "gemini-2.5-flash"
    REASONING_MODEL: str = "gemini-2.5-pro"
    FAST_MODEL: str = "gemini-2.5-flash-lite"
    
    # OpenAI & Anthropic (Optional fallbacks)
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None

    # Search & Data Providers
    TAVILY_API_KEY: Optional[str] = None
    ALPHA_VANTAGE_API_KEY: Optional[str] = None
    DEFAULT_MARKET: str = "IN"  # "IN" for NSE/BSE, "US" for US Equities

    # Storage Settings
    STORAGE_DIR: str = "./data/storage"
    STORAGE_BACKEND: str = "local"  # local | s3 | minio

    # Agent Runtime Settings
    MAX_EVIDENCE_PER_AGENT: int = 20
    VALUATION_DISCOUNT_RATE: float = 0.12  # Default 12% for Indian equities
    DEFAULT_TERMINAL_GROWTH_RATE: float = 0.05  # 5% terminal growth


settings = Settings()
