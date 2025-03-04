from datetime import datetime, timedelta, timezone
import jwt
import os

from auth.hasher import verify_password
from psycopg import AsyncConnection
from db.users import get_user_by_email


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
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
