import psycopg

class DatabaseDocumentManager:
    def __init__(self, conn: psycopg.AsyncConnection):
        self.__conn = conn

    async def insert_document(self, owner_id : int, filepath: str):
        insert_query = "INSERT INTO document_data.documents (owner_id, filepath) VALUES (%s)"
        async with self.__conn.cursor() as cur:
            await cur.execute(insert_query,(owner_id,filepath,)
            )
            await self.__conn.commit()
    
    async def delete_document(self, id: int):
        delete_query = "DELETE FROM document_data.documents WHERE ID = %s"
        async with self.__conn.cursor() as cur:
            await cur.execute(delete_query,(id,))
            await self.__conn.commit()
