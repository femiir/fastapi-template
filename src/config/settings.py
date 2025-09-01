from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, PostgresDsn


class Settings(BaseSettings):
	# Define your settings here
	database_url: PostgresDsn = Field(alias='DATABASE_URL')
	app_name: str = Field(alias='APP_NAME', default='My FastAPI App')
	debug: bool = Field(alias='DEBUG', default=False)

	model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')


@lru_cache()
def get_settings() -> Settings:
	return Settings()


settings = get_settings()
