import psycopg
import numpy as np


class DatabaseChunkManager:
    def __init__(self, conn: psycopg.AsyncConnection):
        self.__conn = conn

    async def insert_chunk(
        self, document_id: int, chunk_text: str, chunk_vector: np.array
    ):
        insert_query = "INSERT INTO document_data.chunks (document_id,chunk_text,chunk_vector) VALUES (%s,%s,%s)"
        async with self.__conn.cursor() as cur:
            await cur.execute(
                insert_query,
                (
                    document_id,
                    chunk_text,
                    chunk_vector.tolist()
                ),
            )
            await self.__conn.commit()

    async def delete_chunk(self, id: int):
        delete_query = "DELETE FROM document_data.chunks WHERE ID = %s"
        async with self.__conn.cursor() as cur:
            await cur.execute(delete_query, (id,))
            await self.__conn.commit()

    async def get_related_chunks(self, vector: np.ndarray):
        select_query = """
                        SELECT *
                        FROM document_data.chunks
                        ORDER BY 1 - (chunk_vector <=> %s::vector) DESC
                        LIMIT 5
                        """
        async with self.__conn.cursor() as cur:
            await cur.execute(select_query, (vector.tolist(),))
            rows = await cur.fetchall()
            return rows
