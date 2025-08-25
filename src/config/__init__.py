from functools import lru_cache
from pydantic import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):

    model_config: SettingsConfigDict = {
        "env_file": ".env",
        "case_sensitive": True
    }



@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()