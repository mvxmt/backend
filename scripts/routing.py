import sys
# sys hacks to get imports to work
sys.path.append('./')

import os
import asyncio
import psycopg
from dotenv import load_dotenv
from contextlib import asynccontextmanager

from db.database_chunks import DatabaseChunkManager
from services.embedding import EmbedManager
from services.context import ContextManager

load_dotenv(".env.example",override=True)

@asynccontextmanager
async def _get_db_connection():
    connection_parameters = {
        'dbname' : 'rag_data',
        'user' : 'postgres',
        'host' : os.environ.get("POSTGRES_HOST"),
        'port' : '5432'
    }
    try:
        conn = await psycopg.AsyncConnection.connect(**connection_parameters)
        yield conn
    except psycopg.Error as e:
        print(f"Error connecting to the database: {e}")
    finally:
        await conn.close()

async def main():
    #Connect to Database
    async with _get_db_connection() as conn:
        em = EmbedManager()
        cm = DatabaseChunkManager(conn)
        ctx = ContextManager()

        prompt = input("Please Enter a Prompt: ") #Replace with request to front end
        embed = await em.embed(prompt)
        results = await cm.get_related_chunks(embed)
        context = ctx.get_context(conn, results)
        print(context) #Replace with answer_prompt(context) from Prompt Manager

if __name__ == "__main__":
    asyncio.run(main())
