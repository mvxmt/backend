import sys

# sys hacks to get imports to work
sys.path.append("./")

import asyncio
from dotenv import load_dotenv
from db.client import get_database_session
from db.database_chunks import DatabaseChunkManager
from services.context import ContextManager
from services.embedding import EmbedManager

load_dotenv(".env.example", override=True)

async def main():
    # Connect to Database
    async for conn in get_database_session():
        em = EmbedManager()
        cm = DatabaseChunkManager(conn)
        ctx = ContextManager()

        prompt = input("Please Enter a Prompt: ")  # Replace with request to front end
        embed = await em.embed(prompt)
        results = await cm.get_related_chunks(embed)
        context = ctx.get_context(conn, results)
        for entry in context:
            print(f"ID: {entry["id"]}\n Text: {entry["text"]}\n")  # Replace with answer_prompt(context) from Prompt Manager


if __name__ == "__main__":
    asyncio.run(main())
