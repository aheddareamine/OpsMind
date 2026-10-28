from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    database_url : str
    secret_key : str
    access_token_expire_minutes : int
    refresh_token_expire_days : int
    algorithm : str

    model_config = SettingsConfigDict(
        env_file="/home/ouimaison/Desktop/Web/FastAPI/OpsMind/.env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False)


@lru_cache
def get_settings():
    return Settings()