import sys

# sys hacks to get imports to work
sys.path.append("./")
from typing import Annotated

from auth.models import UserDBO
from auth.router import get_current_user

import dotenv

from fastapi import  APIRouter, Depends, UploadFile

from db.database_chunks import DatabaseChunkManager
from db.database_documents import DatabaseDocumentManager
from db.client import get_database_session

from .crypto import CryptographyManager
from .embedding import EmbedManager
from .parser import Parser
from config import get_settings

dotenv.load_dotenv()
router = APIRouter(prefix="/file")
settings = get_settings()

async def insert_chunks(conn, document_id: str, chunks: list[str]):
        cm = DatabaseChunkManager(conn)
        em = EmbedManager()
        crypto = CryptographyManager.from_settings(settings)

        for chunk_text in chunks:
            chunk_vector = await em.embed(chunk_text)
            chunk_ciphertext = crypto.encrypt_string(chunk_text)
            await cm.insert_chunk(
                document_id, chunk_ciphertext, chunk_vector
            )


# Main Driver Function, should route what needs to occur
# on document upload.
#Take in a filepath and the filetype
@router.post("/upload", status_code=201)
async def on_upload(user: Annotated[UserDBO, Depends(get_current_user)], src_file : UploadFile):
    async for conn in get_database_session():
        parser = Parser()
        #Get File Name
        source = src_file.filename
        #Insert File Owner and File Name Into DB
        dm = DatabaseDocumentManager(conn)
        source_id = await dm.insert_document(user.id, source)
        #Parse File
        content = await parser.get_document_content(src_file.file,src_file.content_type)
       
        #Delete Temp File
        await src_file.close()

        #Chunk Document
        try:
            chunks =  await parser.get_content_chunks(content)
        except Exception as e:
                print("Error: ",e)
        else:
            #Insert Chunks into DB
            await insert_chunks(conn,source_id,chunks)
