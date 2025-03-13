from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import jwt

from auth.models import User, UserRegistration
from auth.utils import authenticate_user, create_access_token
from config import Settings, get_settings
from db.client import DatabaseConnection
import db.users

router = APIRouter(prefix="/auth")
oauth2_scheme = OAuth2PasswordBearer("/auth/token")


async def get_current_user(
    conn: DatabaseConnection,
    token: Annotated[str, Depends(oauth2_scheme)],
    settings: Annotated[Settings, Depends(get_settings)],
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm.value]
        )
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except jwt.InvalidTokenError:
        raise credentials_exception

    user = await db.users.get_user_by_email(conn, email=email)
    if user is None:
        raise credentials_exception

    return user


@router.post("/token")
async def login_for_access_token(
    conn: DatabaseConnection,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
):
    user = await authenticate_user(conn, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/users/me")
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    return current_user


@router.post("/register")
async def register_user(
    form_data: Annotated[UserRegistration, Form()], conn: DatabaseConnection
):
    await db.users.register_user(conn, form_data)
