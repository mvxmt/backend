import psycopg
from ulid import ULID

class DatabaseDocumentManager:
    def __init__(self, conn: psycopg.AsyncConnection):
        self.__conn = conn

    async def get_document_by_id(self, id: str):
        select_query = "SELECT * FROM document_data.documents WHERE ID = %s"
        async with self.__conn.cursor() as cur:
            await cur.execute(select_query, (id,))
            doc = await cur.fetchall()
            return doc

    async def insert_document(self, owner: int, filename: str):
        insert_query = (
            "INSERT INTO document_data.documents (id, owner, filename) VALUES (%s, %s, %s)"
        )
        doc_id = ULID()
        async with self.__conn.cursor() as cur:
            await cur.execute(
                insert_query,
                (
                    str(doc_id),
                    owner,
                    filename
                ),
            )
            await self.__conn.commit()
            return str(doc_id)


    async def delete_document(self, id: str):
        delete_query = "DELETE FROM document_data.documents WHERE ID = %s"
        async with self.__conn.cursor() as cur:
            await cur.execute(delete_query, (id,))
            await self.__conn.commit()
