"""Basic test for settings and configuration."""
from src.core.config import Settings


def test_settings_initialization():
    settings = Settings(
        APP_NAME="Test Stock Engine",
        POSTGRES_SERVER="localhost",
        POSTGRES_PORT=5432,
        POSTGRES_USER="postgres",
        POSTGRES_PASSWORD="password123",
        POSTGRES_DB="test_db",
    )
    assert settings.APP_NAME == "Test Stock Engine"
    assert settings.sync_database_url == "postgresql://postgres:password123@localhost:5432/test_db"
    assert settings.async_database_url == "postgresql+asyncpg://postgres:password123@localhost:5432/test_db"
    assert settings.DEFAULT_MARKET == "IN"
