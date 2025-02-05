import sys

# sys hacks to get imports to work
sys.path.append("./")

import asyncio
from dotenv import load_dotenv
from db.client import get_database_session
from db.database_chunks import DatabaseChunkManager
from services.context import ContextManager
from services.embedding import EmbedManager
from services.prompt import PromptManager

load_dotenv()

async def main():
    # Connect to Database
    async for conn in get_database_session():
        em = EmbedManager()
        cm = DatabaseChunkManager(conn)
        ctx = ContextManager()
        pm = PromptManager()

        #prompt = input("Please Enter a Prompt: ")  # Replace with request to front end
        prompt = "What is Test Driven Development?"
        embed = await em.embed(prompt)
        results = await cm.get_related_chunks(embed)
        context = ctx.get_context(conn, results)

        approved_context = []
        for entry in context:
            entry['score'],entry['justification'] = await pm.get_relevance(entry["text"],prompt)
            if entry['score'] != 0:
                #context.remove(entry)
                approved_context.append(entry)
        
        raw_answer = await pm.raw_answer(prompt)
        augmented_answer = await pm.load_context(context,prompt)
        print("Raw Answer:\n",raw_answer)
        print("Augmented Answer:\n",augmented_answer)
        print()


if __name__ == "__main__":
    asyncio.run(main())
