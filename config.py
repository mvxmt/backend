from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from enum import Enum

class JWTAlgorithm(Enum):
    HS256 = "HS256"

class Settings(BaseSettings):
    jwt_secret_key: str
    jwt_algorithm: JWTAlgorithm
    jwt_access_token_exp_minutes: int = 30

    model_config = SettingsConfigDict(env_file=".env")

@lru_cache
def get_settings():
    return Settings()
