import pytest
import asyncio
import pytest_asyncio
import ollama
import psycopg
from database_chunks import DatabaseChunkManager

def db_connect(self):
        try:
            return psycopg.AsyncConnection.connect(
            host='localhost',
            dbname='rag_data', 
            user = 'postgres',
            port='5432',
        )
        
        except psycopg.Error as e:
            print(f"Error connecting to the database: {e}")
            return None


class TestDatabaseChunkManager():
    @pytest.mark.asyncio
    async def test_insert_chunk():

        document_id = 1
        chunk_text = """
        TDD’s historical context
        Test-driven development has emerged in conjunction with the rise of agile process
        models. Both have roots in the iterative, incremental, and evolutionary process models used as
        early as the 1950s. In addition, tools have evolved to play a significant role in supporting TDD. 
        """
        chunk_vector = ollama.embed(model='nomic-embed-text', input=f"search_document: {chunk_text}")

        conn = db_connect()
        dbchm = DatabaseChunkManager(conn)
        
        await dbchm.insert_chunk(document_id, chunk_text, chunk_vector)
        
        select_document =  """
                        SELECT *
                        FROM document_data.chunks
                        WHERE document_id = %s AND chunk_text = %s;
                        """
        
        async with conn.cursor() as cur:
            await cur.execute(select_document, (document_id, chunk_text))
            rows = await cur.fetchall()

            assert rows
            assert rows[0][1] == document_id
            assert rows[0][2] == chunk_text
        
        conn.close()
    
    # assuming at least one entry is in the database before hand
    @pytest.mark.asyncio
    async def test_delete_chunk():
         conn = db_connect()
         dbchm = DatabaseChunkManager(conn)

         ID = 1
         
         select_document =  """
                        SELECT *
                        FROM document_data.chunks
                        WHERE ID= %s;
                        """
         
         async with conn.cursor() as cur:
            await cur.execute(select_document, (ID,))
            rows = await cur.fetchall()
            
            assert rows

            await dbchm.delete_chunk(ID)

            await cur.execute(select_document, (ID,))
            rows_after = await cur.fetchall()

            assert not rows_after

    # assuming that test entries are inserted into the database before hand
    @pytest.mark.asyncio
    async def test_get_related_chunks():
        conn = db_connect()
        dbchm = DatabaseChunkManager(conn)

        query = "What is the historical context of TDD?"
        vector = ollama.embed(model='nomic-embed-text', input=f"search_query: {query}")

        results = await dbchm.get_related_chunks(vector)
        document_id = results[0][1]

        assert document_id == 12345
        # when we insert the most similar chunk make sure it has id of 12345






