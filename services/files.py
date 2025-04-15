import sys
from fastapi import HTTPException

from db.client import get_database_session

# sys hacks to get imports to work
sys.path.append("./")

from auth.models import UserDBO
from fastapi import APIRouter, Depends
from typing import Annotated
from auth.router import get_current_user
from db.database_documents import DatabaseDocumentManager, Document

router = APIRouter(prefix="/files", tags=["Files"])

@router.get("/retrieve")
async def all_files_for_user(
    user: Annotated[UserDBO, Depends(get_current_user)]
) -> list[Document]:
    async for conn in get_database_session():
        dm = DatabaseDocumentManager(conn)
        return await dm.get_all_files_for_user(user.id)

@router.delete("/delete/{document_id}")
async def delete_file_by_id(user: Annotated[UserDBO, Depends(get_current_user)],document_id: str):
    async for conn in get_database_session():
        try:
            dm = DatabaseDocumentManager(conn)
            await dm.delete_file_by_id(user.id, document_id)
        except AssertionError:
            raise HTTPException(404)