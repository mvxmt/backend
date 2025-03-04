from typing import Optional
import psycopg
from auth.models import UserRegistration, UserDBO
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
            return UserDBO(id=user[0], name=user[1], email=user[2], password_hash=user[3])
        else:
            return None
