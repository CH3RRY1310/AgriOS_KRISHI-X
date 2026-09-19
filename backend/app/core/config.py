"""Application configuration for the AgriOS API."""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Small typed settings surface for local development and deployment."""

    application_name: str = "AgriOS KRISHI-X API"
    api_version: str = "v1"
    environment: str = "development"
    frontend_origins: list[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]
    database_url: str = "sqlite:///./backend/agrios.db"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def database_path(self) -> Path:
        """Resolve the SQLite file path from the project root in a portable way."""
        resolved = Path(self.database_url.replace("sqlite:///", ""))
        if not resolved.is_absolute():
            cwd = Path.cwd()
            root = cwd.parent if cwd.name == "backend" else cwd
            resolved = (root / resolved).resolve()
        resolved.parent.mkdir(parents=True, exist_ok=True)
        return resolved

    @property
    def database_url_resolved(self) -> str:
        """Return a SQLAlchemy SQLite URL anchored to the actual backend database file."""
        return f"sqlite:///{self.database_path.as_posix()}"


settings = Settings()
