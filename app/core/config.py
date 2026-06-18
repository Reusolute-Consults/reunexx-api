from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Reunexx Core API"
    VERSION: str = "1.0.0"
    
    # Supabase Credentials
    SUPABASE_URL: str
    SUPABASE_ANON_KEY: str
    SUPABASE_SERVICE_ROLE_KEY: str # Used ONLY for system-level overrides (like creating a tenant)
    DATABASE_PASSWORD: Optional[str] = None # For direct DB access if needed (e.g. for migrations)

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()