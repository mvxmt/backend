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
from pydantic import BaseModel
import uuid

class Prompt(BaseModel):
    string:str

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
prompt = ""
em = EmbedManager()
ctx = ContextManager()
pm = PromptManager()

router = APIRouter(prefix="/chat")

@router.post("/prompt")
#async def get_user_input(message:Annotated[str,Form()]):
async def get_user_input(user_prompt:Prompt):
    global prompt
    prompt =  user_prompt.string
    print("Recieved : ",prompt)
    return prompt #{"message" : str(f'Received: {message}')}

async def stream_answer(response:Response):
     for chunk in response.message:
        for letter in chunk:
            yield letter
            await asyncio.sleep(0.01)

@router.get("/reponse")
async def chat():
    global prompt
    print("Submitted Prompt:",prompt)
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
                    graded_entry.score,graded_entry.justification = await pm.get_relevance(entry.text,prompt)
                    if graded_entry.score != 0:
                        approved_context.append(graded_entry)
            except Exception as e:
                print("Error: ",e)
            else:
                print("Context Formatted")

            #INSERT HALLUCINATION CHECK HERE
            
            try:
                print('Answering Prompt...')
                augmented_answer = await pm.load_context(context,prompt)
            except Exception as e:
                print("Error: ",e)
            else:
                print("Stream Received")

            response = Response(id=str(uuid.uuid4()),role='assistant',message=augmented_answer)
    return StreamingResponse(stream_answer(response),media_type='text/event-stream')
