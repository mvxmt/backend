import sys
import uuid
from fastapi import HTTPException

from db.client import DatabaseConnection

# sys hacks to get imports to work
sys.path.append("./")

from auth.models import UserDBO
from fastapi import APIRouter, Depends
from typing import Annotated
from auth.router import get_current_user
import db.chat_history as chat_history_db

router = APIRouter(prefix="/chatHistory", tags=["Chat History"])

@router.get("/all")
async def all_threads_for_user(
    user: Annotated[UserDBO, Depends(get_current_user)], conn: DatabaseConnection
) -> list[chat_history_db.ChatThreadNoData]:
    return await chat_history_db.get_all_chat_thread_for_user(conn, user.id)


@router.get("/thread")
async def thread_by_id(
    user: Annotated[UserDBO, Depends(get_current_user)],
    chat_thread_id: uuid.UUID,
    conn: DatabaseConnection,
) -> chat_history_db.ChatThread:
    ct = await chat_history_db.get_chat_thread_by_user_chat_id(
        conn, user.id, chat_thread_id
    )

    if not ct:
        raise HTTPException(404)

    return ct


@router.put("/appendMessage")
async def append_message_to_thread(
    user: Annotated[UserDBO, Depends(get_current_user)],
    chat_thread_id: uuid.UUID,
    chat_message: chat_history_db.ChatMessage,
    conn: DatabaseConnection,
):
    try:
        await chat_history_db.append_message_to_chat_thread_by_uid_cid(
            conn, user.id, chat_thread_id, chat_message
        )
    except AssertionError:
        raise HTTPException(404)


@router.delete("/delete")
async def delete_chat_thread(
    user: Annotated[UserDBO, Depends(get_current_user)],
    chat_thread_id: uuid.UUID,
    conn: DatabaseConnection,
):
    try:
        await chat_history_db.delete_chat_thread(conn, user.id, chat_thread_id)
    except AssertionError:
        raise HTTPException(404)
    
@router.post("/rename")
async def rename_chat_thread(
    conn: DatabaseConnection,
    user: Annotated[UserDBO, Depends(get_current_user)],
    chat_thread_id: uuid.UUID,
    name: str
):
    try:
        await chat_history_db.set_chat_thread_name_by_uid_cid(conn, user.id, chat_thread_id, name)
    except AssertionError:
        raise HTTPException(404)