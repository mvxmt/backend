import sys

# sys hacks to get imports to work
sys.path.append("./")

import dotenv
from tqdm import tqdm
from db.client import get_database_session
from db.database_chunks import DatabaseChunkManager
from services.context import ContextManager, RAGContext
from services.embedding import EmbedManager
from services.prompt import PromptManager
import db.model_settings as model_settings

from services.crypto import CryptographyManager
from config import Settings, get_settings

from fastapi import APIRouter, Form, Depends
from fastapi.responses import StreamingResponse
from typing import Annotated, Any
from pydantic import BaseModel
#AUTH
from auth.models import UserDBO
from auth.router import maybe_get_current_user


class Response(BaseModel):
    id:str
    role:str
    message:str

class GradedContext():
    id:int
    source:str
    text:str
    grade:int
    justification:str

class Chunk(BaseModel):
    owner:int
    id: int
    source: str
    text:str
    distance:str

class ModelRequest(BaseModel):
    user_prompt:Annotated[str, Form()]
    distance:int
    limit:int
    model:str

class ContextRequest(BaseModel):
    user_prompt:str
    context:list[RAGContext]
    

dotenv.load_dotenv()

router = APIRouter(prefix="/chat", tags=["Chat"])

@router.post("/retrieve")
async def retrieve(
    user_prompt:Annotated[str, Form()],
    settings: Annotated[Settings, Depends(get_settings)],
    user: Annotated[UserDBO | None, Depends(maybe_get_current_user)]
    ):
    em = EmbedManager()
    crypto = CryptographyManager.from_settings(settings)
    ctx = ContextManager(crypto)

    print("Prompt Recieved")
    async for conn in get_database_session():
        #CONNECT TO DB
        try:
            print("Connecting to DB...")
            cm = DatabaseChunkManager(conn)
        except Exception as e:
            print("Error: ",e)
        else:
            print("Conection Succesful")
        #EMBED PROMPT
        try:
            print("Embedding User Prompt...")
            embed = await em.embed(user_prompt)
        except Exception as e:
            print("Error: ",e)
        else:
            print("Embedding Complete")
        #FETCH USER SETTINGS
        try:
            print("Fetching User Settings")
            user_settings = await model_settings.get_users_model_settings(conn,user.id)
        except Exception as e:
            print("Error: ",e)
        else:
            print(f"Settings Fetched: {user_settings.distance}, {user_settings.chunks}")
        #FETCHING CHUNKS
        try:
            print("Fetching Nearby Chunks...")
            results = await cm.get_related_chunks(embed,user.id,user_settings.distance, user_settings.chunks)
        except Exception as e:
            print("Error: ",e)
        else:
            print(f'{len(results)} Chunks Retrieved')
            retrieved_chunks = []
            for result in results:
                chunk = Chunk(
                    owner=result[0],
                    id=result[1],
                    source=result[2],
                    text=result[3],
                    distance=result[4])
                retrieved_chunks.append(chunk)

        try:
            print("Formatting Context...")
            context = ctx.get_context(retrieved_chunks)
        except Exception as e:
            print("Error: ",e)
        else:
            print("Context Formatted")

        return context

@router.post("/grade")
async def grade(
    request:ContextRequest,
    user: Annotated[UserDBO | None, Depends(maybe_get_current_user)],
    ):
    try:
        approved_context = []
        pm = PromptManager()
        print('Grading Relevance...')
        for entry in request.context:
            #Create new graded entry
            graded_entry = GradedContext()
            #Fill with current values
            graded_entry.id = entry.id
            graded_entry.source = entry.source
            graded_entry.text = entry.text
            #Fill new values
            graded_entry.score,graded_entry.justification = await pm.get_relevance(entry.text,request.user_prompt)
            if graded_entry.score != 0:
                approved_context.append(graded_entry)
        print(f"Grading Completed: {len(approved_context)} Chunks Approved")
        return approved_context
    except Exception as e:
        print("Error: ",e)

@router.post("/chat")
async def chat(
    request:ContextRequest,
    user: Annotated[UserDBO | None, Depends(maybe_get_current_user)],
    ):
    if user and len(request.context) > 0:
        async for conn in get_database_session():
            #FETCH USER SETTINGS
            try:
                print("Fetching User Settings")
                user_settings = await model_settings.get_users_model_settings(conn,user.id)
            except Exception as e:
                print("Error: ",e)
            else:
                print(f"Settings Fetched: {user_settings.distance}, {user_settings.chunks}")
            #ANSWER WITH CONTEXT
            try:
                print('Answering Prompt With Context...')
                pm = PromptManager(user_settings.model)
                return StreamingResponse(pm.load_context(request.context,request.user_prompt))
            except Exception as e:
                print("Error: ",e)
    else:
        try:
            pm = PromptManager()
            print('Answering Prompt without Context...')
            return StreamingResponse(pm.raw_answer(request.user_prompt))
        except Exception as e:
            print("Error: ",e)

@router.post("/response")
async def response(
    user_prompt:Annotated[str, Form()],
    settings: Annotated[Settings, Depends(get_settings)],
    user: Annotated[UserDBO | None, Depends(maybe_get_current_user)]
    ):

    em = EmbedManager()
    crypto = CryptographyManager.from_settings(settings)
    ctx = ContextManager(crypto)

    print("Prompt Recieved")
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

            approved_context = []
            if user:
                try:
                    print("Fetching User Settings")
                    settings = await model_settings.get_users_model_settings(conn,user.id)
                    request = ModelRequest(
                        user_prompt=user_prompt,
                        distance=settings.distance,
                        limit=settings.chunks,
                        model=settings.model
                    )
                    pm = PromptManager(request.model)
                except Exception as e:
                    print("Error: ",e)
                else:
                    print(f"Settings Fetched: {settings.distance}, {settings.chunks}, {settings.model}")
                try:
                    print("Fetching Nearby Chunks...")
                    results = await cm.get_related_chunks(embed,user.id,request.distance, request.limit)
                except Exception as e:
                    print("Error: ",e)
                else:
                    print(f'{len(results)} Chunks Retrieved')
                    retrieved_chunks = []
                    for result in results:
                        chunk = Chunk(
                            owner=result[0],
                            id=result[1],
                            source=result[2],
                            text=result[3],
                            distance=result[4])
                        retrieved_chunks.append(chunk)

                try:
                    print("Formatting Context...")
                    context = ctx.get_context(retrieved_chunks) #Decryption would need to happen here
                except Exception as e:
                    print("Error: ",e)
                else:
                    print("Context Formatted")
            
                try:
                    if context:
                        print('Grading Relevance...')
                        for entry in tqdm(context):
                            #Create new graded entry
                            graded_entry = GradedContext()
                            #Fill with current values
                            graded_entry.id = entry.id
                            graded_entry.source = entry.source
                            graded_entry.text = entry.text
                            #Fill new values
                            graded_entry.score,graded_entry.justification = await pm.get_relevance(entry.text,request.user_prompt)
                            if graded_entry.score != 0:
                                approved_context.append(graded_entry)
                        print(f"Grading Completed: {len(approved_context)} Chunks Approved")
                except Exception as e:
                    print("Error: ",e)

                #INSERT HALLUCINATION CHECK HERE

            if user and len(approved_context) > 0:
                try:
                    print('Answering Prompt With Context...')
                    return StreamingResponse(pm.load_context(approved_context,request.user_prompt))
                except Exception as e:
                    print("Error: ",e)
            else:
                try:
                    pm = PromptManager()
                    print('Answering Prompt without Context...')
                    return StreamingResponse(pm.raw_answer(user_prompt))
                except Exception as e:
                    print("Error: ",e)

@router.get("/models")
async def models():
    pm = PromptManager()
    res = await pm.get_local_models()
    models = []
    for info in res.models:
        if "nomic" not in info.model:
            models.append(info.model)
    return models

