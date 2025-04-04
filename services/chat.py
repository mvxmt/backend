import sys

# sys hacks to get imports to work
sys.path.append("./")

import dotenv
from tqdm import tqdm
from db.client import get_database_session
from db.database_chunks import DatabaseChunkManager
from services.context import ContextManager
from services.embedding import EmbedManager
from services.prompt import PromptManager

from services.crypto import CryptographyManager
from config import Settings, get_settings

from fastapi import APIRouter, Form, Depends
from fastapi.responses import StreamingResponse
from typing import Annotated
from pydantic import BaseModel

class Response(BaseModel):
    id:str
    role:str
    message:str

class GradedContext():
    id:int
    source:int
    text:str
    grade:int
    justification:str

dotenv.load_dotenv()

router = APIRouter(prefix="/chat")

@router.post("/response")
async def chat(
    user_prompt:Annotated[str,Form()],
    settings: Annotated[Settings, Depends(get_settings)]
    ):

    em = EmbedManager()
    crypto = CryptographyManager.from_settings(settings)
    ctx = ContextManager(crypto)
    pm = PromptManager()

    print("Submitted Prompt:",user_prompt)
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
                embed = await em.embed(user_prompt)
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
                context = ctx.get_context(results) #Decryption would need to happen here
            except Exception as e:
                print("Error: ",e)
            else:
                print("Context Formatted")
        
            try:
                print('Grading Relevance...')
                approved_context = []
                for entry in tqdm(context):
                    #Create new graded entry
                    graded_entry = GradedContext()
                    #Fill with current values
                    graded_entry.id = entry.id
                    graded_entry.source = entry.source
                    graded_entry.text = entry.text
                    #Fill new values
                    graded_entry.score,graded_entry.justification = await pm.get_relevance(entry.text,user_prompt)
                    if graded_entry.score != 0:
                        approved_context.append(graded_entry)
            except Exception as e:
                print("Error: ",e)
            else:
                print("Context Formatted")

            #INSERT HALLUCINATION CHECK HERE

            if len(approved_context) > 0:
                try:
                    print('Answering Prompt With Context...')
                    #answer = await pm.load_context(context,user_prompt)
                    #response = Response(id=str(uuid.uuid4()),role='assistant',message=answer)
                    return StreamingResponse(pm.load_context(context,user_prompt))
                except Exception as e:
                    print("Error: ",e)
            else:
                try:
                    print('Answering Prompt without Context...')
                    #answer = await pm.raw_answer(user_prompt)
                    return StreamingResponse(pm.raw_answer(user_prompt))
                except Exception as e:
                    print("Error: ",e)
