import sys
from fastapi import HTTPException

from db.client import DatabaseConnection

# sys hacks to get imports to work
sys.path.append("./")

from auth.models import UserDBO
from fastapi import APIRouter, Depends
from typing import Annotated
from auth.router import get_current_user
import db.model_settings as model_settings


router = APIRouter(prefix="/settings", tags=["Settings"])

@router.get("/get")
async def get(
    user: Annotated[UserDBO, Depends(get_current_user)], 
    conn: DatabaseConnection):
        return await model_settings.get_users_model_settings(conn, user.id)

# @router.get("/add_model_settings")
# async def create_user_settings(
#     conn: DatabaseConnection, settings:model_settings.ModelSettings):
#     return await model_settings.add_new_model_settings(conn,settings)

@router.post("/save")
async def save(
    user: Annotated[UserDBO, Depends(get_current_user)], conn: DatabaseConnection, settings:model_settings.ModelSettings):
    current_settings = await model_settings.get_users_model_settings(conn, user.id)
    if current_settings is None:
        return await model_settings.add_new_model_settings(conn,user.id,settings)
    return await model_settings.update_users_model_settings(conn,user.id,settings)