import psycopg
from pydantic import BaseModel

class Document(BaseModel):
    id:int
    owner:int
    filename:str


async def get_all_files_for_user(
    conn: psycopg.AsyncConnection, user_id: int
) -> list[Document]:
    f = await conn.execute(
        "SELECT * FROM document_data.documents WHERE owner = %s",
        (user_id,),
    )

    files: list[Document] = []

    for e in await f.fetchall():
        files.append(
            Document(
                id=e[0],
                owner=e[1],
                filename=e[2],
            )
        )
    return files