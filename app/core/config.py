from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Enterprise AI Model Selection Optimizer"
    app_env: str = "development"
    app_host: str = "127.0.0.1"
    app_port: int = 8000
    log_level: str = "INFO"
    database_url: str = (
        "postgresql+psycopg2://postgres:postgres@localhost:5432/model_optimizer"
    )

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
