import psycopg
import numpy as np


class DatabaseChunkManager:
    def __init__(self, conn: psycopg.AsyncConnection):
        self.__conn = conn

    async def insert_chunk(
        self, source_id: str, chunk_text: str, chunk_vector: np.array
    ):
        insert_query = "INSERT INTO document_data.chunks (source_id,chunk_text,chunk_vector) VALUES (%s,%s,%s)"
        async with self.__conn.cursor() as cur:
            await cur.execute(
                insert_query,
                (source_id, chunk_text, chunk_vector.tolist()),
            )
            await self.__conn.commit()

    async def delete_chunk(self, id: int):
        delete_query = "DELETE FROM document_data.chunks WHERE ID = %s"
        async with self.__conn.cursor() as cur:
            await cur.execute(delete_query, (id,))
            await self.__conn.commit()

    async def get_related_chunks(
            self, 
            vector: np.ndarray, 
            user_id:int,
            distance:float=0.5,):
        select_query = """
                SELECT document_data.documents.owner as owner, document_data.chunks.id, source_id, chunk_text, chunk_vector, chunk_vector <=> %s::vector as distance
                FROM document_data.chunks
                WHERE chunk_vector <=> %s::vector < %s::float
                JOIN document_data.documents on document_data.chunks.source_id = document_data.documents.id
                WHERE owner = %s::int
                ORDER BY 1 - (chunk_vector <=> %s::vector) DESC
                LIMIT 10
                        """
        async with self.__conn.cursor() as cur:
            await cur.execute(select_query, (vector.tolist(),vector.tolist(),distance,user_id,vector.tolist(),))
            rows = await cur.fetchall()
            return rows
