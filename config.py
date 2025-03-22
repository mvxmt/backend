from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, model_validator
from enum import Enum
import base64


class JWTAlgorithm(Enum):
    HS256 = "HS256"


class Settings(BaseSettings):
    jwt_secret_key: str
    jwt_algorithm: JWTAlgorithm
    jwt_access_token_exp_minutes: int = 30
    jwt_refresh_token_exp_days: int = 365

    postgres_host: str
    postgres_user: str
    postgres_password: str | None = None
    postgres_database: str

    fernet_keys: list[str] = Field(..., min_length=1)

    model_config = SettingsConfigDict(env_file=".env", extra='ignore')

    @model_validator(mode='after')
    def check_fernet_keys(self) -> "Settings":
        if not all(len(base64.b64decode(a)) == 32 for a in self.fernet_keys):
            raise ValueError('Each fernet key must be 32 byte base64 strings')
        return self


@lru_cache
def get_settings():
    return Settings()
