from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str = "postgresql://lenny_user:lenny_password@localhost:5432/lenny_db"
    environment: str = "development"
    llm_provider: str = "ollama"
    ollama_base_url: str = "http://localhost:11434"
    anthropic_api_key: str = ""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
