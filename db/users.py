from datetime import datetime
from typing import Optional
import psycopg
from auth.models import RefreshTokenInfo, UserRegistration, UserDBO
from auth.hasher import get_password_hash


async def register_user(conn: psycopg.AsyncConnection, reg: UserRegistration):
    async with conn.cursor() as cur:
        await cur.execute(
            "INSERT INTO user_data.users (name, email, password_hash) VALUES (%s, %s, %s)",
            (
                reg.name,
                reg.email,
                get_password_hash(reg.password),
            ),
        )
        await conn.commit()


async def insert_session(
    conn: psycopg.AsyncConnection, token: str, expires_at: datetime, user_id: int
):
    async with conn.cursor() as cur:
        await cur.execute(
            "INSERT INTO user_data.sessions (token, expires_at, user_id) VALUES (%s, %s, %s)",
            (token, expires_at, user_id),
        )
        await conn.commit()


async def refresh_session_expiry(
    conn: psycopg.AsyncConnection, token: str, new_expires_at: datetime
):
    async with conn.cursor() as cur:
        await cur.execute(
            "UPDATE user_data.sessions SET expires_at = %s WHERE token = %s",
            (
                new_expires_at,
                token,
            ),
        )
        await conn.commit()
    


async def get_refresh_token(conn: psycopg.AsyncConnection, token: str):
    async with conn.cursor() as cur:
        await cur.execute(
            "SELECT (token, expires_at, user_id) FROM user_data.sessions WHERE token = %s",
            (token,),
        )
        (db_token,) = await cur.fetchone()

        if db_token:
            return RefreshTokenInfo(
                token=db_token[0], exp=db_token[1], user_id=db_token[2]
            )
        else:
            return None


async def get_user_by_email(
    conn: psycopg.AsyncConnection, email: str
) -> Optional[UserDBO]:
    async with conn.cursor() as cur:
        await cur.execute(
            "SELECT (id, name, email, password_hash) FROM user_data.users WHERE email = %s",
            (email,),
        )
        (user,) = await cur.fetchone()

        if user:
            return UserDBO(
                id=user[0], name=user[1], email=user[2], password_hash=user[3]
            )
        else:
            return None


async def get_user_by_id(conn: psycopg.AsyncConnection, id: int) -> Optional[UserDBO]:
    async with conn.cursor() as cur:
        await cur.execute(
            "SELECT (id, name, email, password_hash) FROM user_data.users WHERE id = %s",
            (id,),
        )
        (user,) = await cur.fetchone()

        if user:
            return UserDBO(
                id=user[0], name=user[1], email=user[2], password_hash=user[3]
            )
        else:
            return None
