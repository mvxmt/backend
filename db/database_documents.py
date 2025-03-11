import psycopg
import os


class DatabaseDocumentManager:
    def __init__(self, conn: psycopg.AsyncConnection):
        self.__conn = conn

    async def get_document_by_id(self, id: int):
        select_query = "SELECT * FROM document_data.documents WHERE ID = %s"
        async with self.__conn.cursor() as cur:
            await cur.execute(select_query, (id,))
            doc = await cur.fetchall()
            return doc

    async def insert_document(self, owner: int, filename: str):
        insert_query = (
            "INSERT INTO document_data.documents (owner, filename) VALUES (%s, %s) RETURNING id"
        )
        async with self.__conn.cursor() as cur:
            await cur.execute(
                insert_query,
                (
                    owner,
                    filename
                ),
            )
            doc_id = (await cur.fetchone())[0]
            await self.__conn.commit()
            return doc_id


    async def delete_document(self, id: int):
        delete_query = "DELETE FROM document_data.documents WHERE ID = %s"
        async with self.__conn.cursor() as cur:
            await cur.execute(delete_query, (id,))
            await self.__conn.commit()
