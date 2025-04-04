import psycopg
from pydantic import BaseModel

class Document(BaseModel):
    id:str
    owner:int
    filename:str


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

    async def get_all_files_for_user(self,user_id: int) -> list[Document]:
        sel_query="SELECT * FROM document_data.documents WHERE owner = %s"
        async with self.__conn.cursor() as cur:
            await cur.execute(sel_query,(user_id,),)
            files: list[Document] = []
            results = await cur.fetchall()
            for file in results:
                files.append(
                    Document(
                        id=file[0],
                        owner=file[1],
                        filename=file[2],
                    )
                )
        return files

    async def delete_file_by_id(self, user_id:int, document_id: str):
        del_query = "DELETE FROM document_data.documents WHERE id=%s AND document_id=%s"
        async with self.__conn.cursor() as cur:
            await cur.execute(
                del_query,
                (user_id,
                document_id,),
            )
        await self.__conn.commit()