import sys
from fastapi import HTTPException

from db.client import DatabaseConnection

# sys hacks to get imports to work
sys.path.append("./")

from auth.models import UserDBO
from fastapi import APIRouter, Depends
from typing import Annotated
from auth.router import get_current_user
import db.files as files_db

router = APIRouter(prefix="/files", tags=["File Retrieval"])

@router.get("/retrieve")
async def all_files_for_user(
    user: Annotated[UserDBO, Depends(get_current_user)], conn: DatabaseConnection
) -> list[files_db.Document]:
    return await files_db.get_all_files_for_user(conn,user.id)