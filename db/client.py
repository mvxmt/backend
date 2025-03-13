from typing import Annotated
from fastapi import Depends
import psycopg
import config


async def get_database_session():
    settings = config.get_settings()
    async with await psycopg.AsyncConnection.connect(
        f"dbname={settings.postgres_database} user={settings.postgres_user} password={settings.postgres_password} host={settings.postgres_host}"
    ) as conn:
        yield conn


DatabaseConnection = Annotated[psycopg.AsyncConnection, Depends(get_database_session)]
