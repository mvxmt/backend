import asyncio
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
import db.model_settings as model_settings

from services.crypto import CryptographyManager
from config import Settings, get_settings

from fastapi import APIRouter, Form, Depends
from fastapi.responses import StreamingResponse
from typing import Annotated
from pydantic import BaseModel

# AUTH
from auth.models import UserDBO
from auth.router import maybe_get_current_user


class Response(BaseModel):
    id: str
    role: str
    message: str


class GradedContext:
    id: int
    source: str
    text: str
    grade: int
    justification: str


class Chunk(BaseModel):
    owner: int
    id: int
    source: str
    text: str
    distance: str


class ModelRequest(BaseModel):
    user_prompt: Annotated[str, Form()]
    distance: int
    limit: int
    model: str


dotenv.load_dotenv()

router = APIRouter(prefix="/chat", tags=["Chat"])


async def preprocess(userID: int, prompt: str, settings: Settings):
    em = EmbedManager()
    crypto = CryptographyManager.from_settings(settings)
    ctx = ContextManager(crypto)

    print("Prompt Submitted")
    async for conn in get_database_session():
        try:
            cm = DatabaseChunkManager(conn)
        except Exception as e:
            print("Error: ", e)

        try:
            embed = await em.embed(prompt)
        except Exception as e:
            print("Error: ", e)

        if userID:
            user_settings = await model_settings.get_users_model_settings(conn, userID)
            try:
                results = await cm.get_related_chunks(
                    embed, userID, user_settings.distance, user_settings.chunks
                )
            except Exception as e:
                print("Error: ", e)
            else:
                print(f"{len(results)} Chunks Retrieved")
                retrieved_chunks = []
                for result in results:
                    chunk = Chunk(
                        owner=result[0],
                        id=result[1],
                        source=result[2],
                        text=result[3],
                        distance=result[4],
                    )
                    retrieved_chunks.append(chunk)

            try:
                context = ctx.get_context(retrieved_chunks)
            except Exception as e:
                print("Error: ", e)

            try:
                approved_context = []
                if context and user_settings.grading:
                    print("Grading Relevance...")
                    pm = PromptManager(grading_model=user_settings.grading_model)
                    for entry in context:
                        # Create new graded entry
                        graded_entry = GradedContext()
                        # Fill with current values
                        graded_entry.id = entry.id
                        graded_entry.source = entry.source
                        graded_entry.text = entry.text
                        # Fill new values
                        (
                            graded_entry.score,
                            graded_entry.justification,
                        ) = await pm.get_relevance(entry.text, prompt)
                        if graded_entry.score != 0:
                            approved_context.append(graded_entry)
                            print(graded_entry.text)
                    print(f"Grading Completed: {len(approved_context)} Chunks Approved")
                    context = approved_context
            except Exception as e:
                print("Error: ", e)

    return context, user_settings


async def stream(userID: int, prompt: str, settings: Settings):
    yield "\u200b\n\n"
    await asyncio.sleep(0.1)

    context, user_settings = await preprocess(userID, prompt, settings)

    yield f"**{user_settings.model}**:\n\n"
    await asyncio.sleep(0.1)
    pm = PromptManager(model=user_settings.model)

    if len(context) > 0:
        try:
            # print('Answering Prompt With Context...')
            yield "*Answering with Context:* \n\n"
            await asyncio.sleep(0.1)
            async for update in pm.load_context(context, prompt):
                yield update
        except Exception as e:
            print("Error: ", e)
    else:
        try:
            # print('Answering Prompt without Context...')
            yield "*No Relevant Context Found:* \n\n"
            async for update in pm.raw_answer(prompt):
                yield update
        except Exception as e:
            print("Error: ", e)


@router.post("/chat")
async def chat(
    user_prompt: Annotated[str, Form()],
    settings: Annotated[Settings, Depends(get_settings)],
    user: Annotated[UserDBO | None, Depends(maybe_get_current_user)],
):
    if user:
        return StreamingResponse(stream(user.id, user_prompt, settings))
    else:
        pm = PromptManager()
        return StreamingResponse(pm.raw_answer(user_prompt))


@router.post("/response")
async def response(
    user_prompt: Annotated[str, Form()],
    settings: Annotated[Settings, Depends(get_settings)],
    user: Annotated[UserDBO | None, Depends(maybe_get_current_user)],
):
    em = EmbedManager()
    crypto = CryptographyManager.from_settings(settings)
    ctx = ContextManager(crypto)

    print("Submitted Prompt:", user_prompt)
    async for conn in get_database_session():
        try:
            print("Connecting to DB...")
            cm = DatabaseChunkManager(conn)
        except Exception as e:
            print("Error: ", e)
        else:
            print("Conection Succesful")

        try:
            print("Embedding User Prompt...")
            embed = await em.embed(user_prompt)
        except Exception as e:
            print("Error: ", e)
        else:
            print("Embedding Complete")

        approved_context = []
        if user:
            settings = await model_settings.get_users_model_settings(conn, user.id)
            request = ModelRequest(
                user_prompt=user_prompt,
                distance=settings.distance,
                limit=settings.chunks,
                model=settings.model,
            )
            pm = PromptManager(request.model)
            try:
                print("Fetching Nearby Chunks...")
                results = await cm.get_related_chunks(
                    embed, user.id, request.distance, request.limit
                )
            except Exception as e:
                print("Error: ", e)
            else:
                print(f"{len(results)} Chunks Retrieved")
                retrieved_chunks = []
                for result in results:
                    chunk = Chunk(
                        owner=result[0],
                        id=result[1],
                        source=result[2],
                        text=result[3],
                        distance=result[4],
                    )
                    retrieved_chunks.append(chunk)

            try:
                print("Formatting Context...")
                context = ctx.get_context(
                    retrieved_chunks
                )  # Decryption would need to happen here
            except Exception as e:
                print("Error: ", e)
            else:
                print("Context Formatted")

            try:
                if context:
                    print("Grading Relevance...")
                    for entry in tqdm(context):
                        # Create new graded entry
                        graded_entry = GradedContext()
                        # Fill with current values
                        graded_entry.id = entry.id
                        graded_entry.source = entry.source
                        graded_entry.text = entry.text
                        # Fill new values
                        (
                            graded_entry.score,
                            graded_entry.justification,
                        ) = await pm.get_relevance(entry.text, request.user_prompt)
                        if graded_entry.score != 0:
                            approved_context.append(graded_entry)
                    print(f"Grading Completed: {len(approved_context)} Chunks Approved")
            except Exception as e:
                print("Error: ", e)

            # INSERT HALLUCINATION CHECK HERE

        if user and len(approved_context) > 0:
            try:
                print("Answering Prompt With Context...")
                return StreamingResponse(
                    pm.load_context(approved_context, request.user_prompt)
                )
            except Exception as e:
                print("Error: ", e)
        else:
            try:
                pm = PromptManager()
                print("Answering Prompt without Context...")
                return StreamingResponse(pm.raw_answer(user_prompt))
            except Exception as e:
                print("Error: ", e)


@router.get("/models")
async def models():
    pm = PromptManager()
    res = await pm.get_local_models()
    size_filter = 3
    models = []
    for info in res.models:
        if "nomic" not in info.model and "B" in info.details.parameter_size:
            size = info.details.parameter_size.split("B")
            size = float(size[0])
            if size > size_filter:
                models.append(info.model)
    return models


@router.get("/grading")
async def grading_models():
    pm = PromptManager()
    res = await pm.get_local_models()
    size_filter = 3
    models = []
    for info in res.models:
        if "nomic" not in info.model and "B" in info.details.parameter_size:
            size = info.details.parameter_size.split("B")
            size = float(size[0])
            if size < size_filter:
                models.append(info.model)
        elif "nomic" not in info.model and "M" in info.details.parameter_size:
            models.append(info.model)
    return models
