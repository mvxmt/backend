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

    async def get_document_by_filename(self, filename: int):
        dir = os.getenv("DATA_DIR")
        path = str(dir + filename)
        select_query = "SELECT * FROM document_data.documents WHERE FILEPATH = %s"
        async with self.__conn.cursor() as cur:
            await cur.execute(select_query, (path,))
            doc = await cur.fetchall()
            return doc

    async def insert_document(self, owner: int, filepath: str, size: int, filename: str):
        insert_query = (
            "INSERT INTO document_data.documents (owner, filepath, size, filename) VALUES (%s, %s, %s, %s)"
        )
        async with self.__conn.cursor() as cur:
            await cur.execute(
                insert_query,
                (
                    owner,
                    filepath,
                    size,
                    filename
                ),
            )
            await self.__conn.commit()

    async def delete_document(self, id: int):
        delete_query = "DELETE FROM document_data.documents WHERE ID = %s"
        async with self.__conn.cursor() as cur:
            await cur.execute(delete_query, (id,))
            await self.__conn.commit()
