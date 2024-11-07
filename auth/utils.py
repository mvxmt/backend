from datetime import datetime, timedelta, timezone
from typing import Annotated
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
import jwt
from passlib.context import CryptContext
import os

from auth.models import UserDBO

# To get these config options run
# docker run -it --entrypoint kratos oryd/kratos:v0.5 hashers argon2 calibrate 1s
pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto",
    argon2__parallelism=16,
    argon2__memory_cost=2097152,
    argon2__rounds=1,
    argon2__digest_size=32,
)

fake_users_db = {
    "johndoe@example.com": {
        "username": "johndoe",
        "name": "John Doe",
        "email": "johndoe@example.com",
        "password_hash": "$argon2i$v=19$m=16,t=2,p=1$NDNwaFc2amRUUTVTYmticw$T7p0bSjoyhHZjHAo09PShg",
        "disabled": False,
    }
}

def verify_password(plaintext: str, hashed_password: str):
    return pwd_context.verify(plaintext, hashed_password)


def get_password_hash(pwd: str):
    return pwd_context.hash(pwd)

def get_user(db, email: str):
    if email in db:
        user_dict = db[email]
        return UserDBO(**user_dict)

def authenticate_user(fake_db, username: str, password: str):
    user = get_user(fake_db, username)
    if not user:
        return False
    if not verify_password(password, user.password_hash):
        return False
    return user

def create_access_token(data: dict, expires_delta: timedelta | None = timedelta(minutes=int(os.environ["JWT_ACCESS_TOKEN_EXP_MINUTES"]))):
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