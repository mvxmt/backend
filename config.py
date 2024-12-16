from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from enum import Enum


class JWTAlgorithm(Enum):
    HS256 = "HS256"


class Settings(BaseSettings):
    jwt_secret_key: str
    jwt_algorithm: JWTAlgorithm
    jwt_access_token_exp_minutes: int = 30

    postgres_host: str
    postgres_user: str
    postgres_password: str | None = None
    postgres_database: str

    model_config = SettingsConfigDict(env_file=".env", extra='ignore')


@lru_cache
def get_settings():
    return Settings()
