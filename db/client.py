from functools import cache
from typing import Annotated
from fastapi import Depends
import psycopg
import asyncio
import config


async def get_database_session():
    settings = config.get_settings()
    async with await psycopg.AsyncConnection.connect(
        f"dbname={settings.postgres_database} user={settings.postgres_user} password={settings.postgres_password} host={settings.postgres_host}"
    ) as conn:
        yield conn

SessionDep = Annotated[psycopg.AsyncConnection, Depends(get_database_session)]