"""Application configuration."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Environment-based application settings."""

    database_url: str = "mysql+pymysql://root:password@localhost:3306/cemede_capacidad_carga"
    secret_key: str = "change-this-secret-key-in-production"
    access_token_expire_minutes: int = 480
    cors_origins: str = "http://localhost:5173,http://localhost:3000"
    api_prefix: str = "/api"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    def get_cors_origins(self) -> list[str]:
        """Return parsed CORS origin list."""
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


settings = Settings()
