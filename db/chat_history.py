import psycopg
import uuid
from pydantic import BaseModel, TypeAdapter
from typing import Literal
from ulid import ULID

class ChatMessage(BaseModel):
    id: ULID
    role: Literal["assistant", "user"]
    message: str


class ChatThreadNoData(BaseModel):
    id: uuid.UUID
    name: str


class ChatThread(ChatThreadNoData):
    id: uuid.UUID
    name: str
    thread: list[ChatMessage]


ChatMessageListAdapter = TypeAdapter(list[ChatMessage])


async def get_all_chat_thread_for_user(
    conn: psycopg.AsyncConnection, user_id: int
) -> list[ChatThreadNoData]:
    ch = await conn.execute(
        "SELECT (chat_thread_id, name) FROM user_data.chat_threads WHERE user_id = %s ORDER BY modified_at",
        (user_id,),
    )

    threads: list[ChatThreadNoData] = []

    for (e,) in await ch.fetchall():
        threads.append(
            ChatThreadNoData(
                id=e[0],
                name=e[1],
            )
        )
    return threads


async def get_chat_thread_by_user_chat_id(
    conn: psycopg.AsyncConnection, user_id: int, chat_id: uuid.UUID
):
    ch = await conn.execute(
        "SELECT (chat_thread_id, name, thread_data) FROM user_data.chat_threads WHERE user_id = %s AND chat_thread_id = %s",
        (user_id, chat_id),
    )

    row = await ch.fetchone()

    if row:
        data = row[0]
        return ChatThread(
            id=data[0],
            name=data[1],
            thread=ChatMessageListAdapter.validate_json(data[2]),
        )

    return None


async def append_message_to_chat_thread_by_uid_cid(
    conn: psycopg.AsyncConnection, user_id: int, chat_id: uuid.UUID, msg: ChatMessage
):
    ct = await get_chat_thread_by_user_chat_id(conn, user_id, chat_id)
    if not ct:
        raise AssertionError()

    ct.thread.append(msg)
    await conn.execute(
        "UPDATE user_data.chat_threads SET thread_data = %s::jsonb WHERE user_id = %s AND chat_thread_id = %s",
        (ChatMessageListAdapter.dump_json(ct.thread).decode(), user_id, chat_id),
    )

async def delete_chat_thread(conn: psycopg.AsyncConnection, user_id: int, chat_id: uuid.UUID):
    async with conn.cursor() as curr:
        await curr.execute(
            "DELETE FROM user_data.chat_threads WHERE user_id = %s AND chat_thread_id = %s",
            (user_id, chat_id),
        )

        if curr.rowcount == 0:
            raise AssertionError()
