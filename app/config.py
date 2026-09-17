from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    provider: str = "mock"
    model: str = "demo"
    api_key: str | None = None
    model_config = SettingsConfigDict(env_file=".env", env_prefix="AI_", extra="ignore")

settings = Settings()
