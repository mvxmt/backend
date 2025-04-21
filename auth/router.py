from datetime import timedelta
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status, Form
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import jwt

from auth.models import RefreshTokenInfo, User, UserDBO, UserRegistration
from auth.utils import authenticate_user, create_access_token, create_refresh_token, refresh_token_expiry
from config import Settings, get_settings
from db.client import DatabaseConnection
import db.users

router = APIRouter(prefix="/auth", tags=["Auth"])
oauth2_scheme = OAuth2PasswordBearer("/auth/token")

REFRESH_TOKEN_COOKIE = "refresh_token"

async def maybe_get_current_user(
    conn: DatabaseConnection,
    token: Annotated[str, Depends(oauth2_scheme)],
    settings: Annotated[Settings, Depends(get_settings)],
):
    try:
        payload = jwt.decode(
            token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm.value]
        )
        id: str = payload.get("sub")
        if id is None:
            return None
    except jwt.InvalidTokenError:
        return None

    user = await db.users.get_user_by_id(conn, int(id))
    return user

async def get_current_user(
    user: Annotated[UserDBO | None, Depends(maybe_get_current_user)]
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not user:
        raise credentials_exception
    
    return user

async def get_refresh_token(conn: DatabaseConnection, req: Request) -> RefreshTokenInfo:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )

    refresh_token = req.cookies.get("refresh_token")
    if not refresh_token:
        raise credentials_exception

    db_refresh_token = await db.users.get_session_token(conn, refresh_token)

    if not db_refresh_token:
        raise credentials_exception

    return db_refresh_token


@router.post("/token")
async def login_for_access_token(
    response: Response,
    conn: DatabaseConnection,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    settings: Annotated[Settings, Depends(get_settings)],
):
    user = await authenticate_user(conn, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = await create_refresh_token(
        conn, timedelta(days=settings.refresh_token_exp_days), user.id
    )

    response.set_cookie(
        REFRESH_TOKEN_COOKIE,
        value=refresh_token.token,
        httponly=True,
        samesite="lax",
        expires=refresh_token.exp
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/refresh")
async def refresh_all_tokens(
    res: Response,
    refresh_token: Annotated[RefreshTokenInfo, Depends(get_refresh_token)],
    conn: DatabaseConnection,
    settings: Annotated[Settings, Depends(get_settings)],
):
    new_token = await refresh_token_expiry(conn, refresh_token, timedelta(days=settings.refresh_token_exp_days))

    if not new_token:
        raise HTTPException(500)

    res.set_cookie(
        key=REFRESH_TOKEN_COOKIE,
        value=new_token.token,
        httponly=True,
        samesite="lax",
        expires=new_token.exp
    )
    access_token = create_access_token(data={"sub": str(refresh_token.user_id)})

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.post("/logout")
async def logout(
    res: Response,
    refresh_token: Annotated[RefreshTokenInfo, Depends(get_refresh_token)],
    conn: DatabaseConnection,
):
    await db.users.delete_session(conn, refresh_token.token)
    res.delete_cookie(REFRESH_TOKEN_COOKIE)


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
