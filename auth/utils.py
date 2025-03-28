from datetime import datetime, timedelta, timezone
import jwt
import os

from auth.hasher import verify_password
from psycopg import AsyncConnection
from auth.models import RefreshTokenInfo, UserDBO
from db.users import get_user_by_email, insert_session, update_session_expiry, get_session_token
import secrets


async def authenticate_user(conn: AsyncConnection, email: str, password: str):
    user = await get_user_by_email(conn, email)
    if not user:
        return False
    if not verify_password(password, user.password_hash):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    if not expires_delta:
        expires_delta = timedelta(
            minutes=int(os.environ["JWT_ACCESS_TOKEN_EXP_MINUTES"])
        )

    SECRET_KEY = os.environ["JWT_SECRET_KEY"]
    ALGORITHM = os.environ["JWT_ALGORITHM"]

    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire, "iat": datetime.now(timezone.utc)})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def refresh_token_expiry(conn: AsyncConnection, refresh_token: RefreshTokenInfo, expires_delta: timedelta):
    await update_session_expiry(
        conn,
        refresh_token.token,
        datetime.now(timezone.utc) + expires_delta,
    )

    return await get_session_token(conn, refresh_token.token)

async def create_refresh_token(conn: AsyncConnection, expires_delta: timedelta, user_id: int) -> RefreshTokenInfo:
    token = secrets.token_hex(16)

    return await insert_session(
        conn,
        token,
        datetime.now(timezone.utc) + expires_delta,
        user_id
    )
    # if not expires_delta:
    #     expires_delta = timedelta(
    #         days=int(os.environ["JWT_REFRESH_TOKEN_EXP_DAYS"])
    #     )

    # SECRET_KEY = os.environ["JWT_SECRET_KEY"]
    # ALGORITHM = os.environ["JWT_ALGORITHM"]

    # to_encode = data.copy()
    # if expires_delta:
    #     expire = datetime.now(timezone.utc) + expires_delta
    # else:
    #     expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    # to_encode.update({"exp": expire, "iat": datetime.now(timezone.utc)})
    # encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    # return encoded_jwt