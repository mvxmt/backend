import sys

# sys hacks to get imports to work
sys.path.append("./")

import asyncio
import dotenv
from tqdm import tqdm
from db.client import get_database_session
from db.database_chunks import DatabaseChunkManager
from services.context import ContextManager
from services.embedding import EmbedManager
from services.prompt import PromptManager


from fastapi import APIRouter, Form
from fastapi.responses import StreamingResponse
from typing import Annotated

dotenv.load_dotenv()
prompt = ""
em = EmbedManager()
ctx = ContextManager()
pm = PromptManager()

router = APIRouter(prefix="/chat")

@router.post("/prompt")
async def get_user_input(message:Annotated[str,Form()]):
    global prompt
    prompt = message
    return {"message" : str(f'Received: {message}')}

async def stream_answer(stream):
     for chunk in stream:
        for letter in chunk:
            yield letter
            await asyncio.sleep(0.01)

@router.get("/reponse")
async def chat():
    global prompt
    async for conn in get_database_session():
            try:
                print("Connecting to DB...")
                cm = DatabaseChunkManager(conn)
            except Exception as e:
                print("Error: ",e)
            else:
                print("Conection Succesful")

            try:
                print("Embedding User Prompt...")
                embed = await em.embed(prompt)
            except Exception as e:
                print("Error: ",e)
            else:
                print("Embedding Complete")

            try:
                print("Fetching Nearby Chunks...")
                results = await cm.get_related_chunks(embed)
            except Exception as e:
                print("Error: ",e)
            else:
                print(f'{len(results)} Chunks Retrieved')

            try:
                print("Formatting Context...")
                context = ctx.get_context(results)
            except Exception as e:
                print("Error: ",e)
            else:
                print("Context Formatted")

            try:
                print('Grading Relevance...')
                approved_context = []
                for entry in tqdm(context):
                    entry['score'],entry['justification'] = await pm.get_relevance(entry["text"],prompt)
                    if entry['score'] != 0:
                        approved_context.append(entry)
            except Exception as e:
                print("Error: ",e)
            else:
                print("Context Formatted")
            
            try:
                print('Answering Prompt...')
                augmented_answer = await pm.load_context(context,prompt)
            except Exception as e:
                print("Error: ",e)
            else:
                print("Stream Received")
    return StreamingResponse(stream_answer(augmented_answer),media_type='text/event-stream')
