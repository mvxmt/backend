import sys

# sys hacks to get imports to work
sys.path.append("./")

import dotenv
import tempfile
#import pathlib

from psycopg import AsyncConnection

from fastapi import  APIRouter, Form, Depends, UploadFile

from db.database_chunks import DatabaseChunkManager as cm
from db.database_documents import DatabaseDocumentManager as dm

from .crypto import CryptographyManager as crypto
from .embedding import EmbedManager as em
from .parser import Parser as parser


dotenv.load_dotenv()
router = APIRouter(prefix="/file")

    #DEPRECATED
    #async def insert_uploaded_document(self, src_file: str, user_id: int):
    #    data_dir = pathlib.Path(path)
    #    p = data_dir / src_file
    #
    #   if p.exists() and p.is_file():
    #       await dm.insert_document(user_id, src_file)

async def insert_chunks(document_id: int, chunks: list[str]):
    for chunk_text in chunks:
        chunk_vector = await em.embed(chunk_text)
        chunk_ciphertext = crypto.encrypt_bytes(chunk_text.encode())
        await cm.insert_chunk(
            document_id, chunk_ciphertext.decode(), chunk_vector
        )

# Documents should still be assigned an ID to keep track of
# the source document and organize chunks
async def get_document_id(filename: str):
    # Get Inserted Documents ID
    doc = await dm.get_document_by_filename(filename)
    return doc[0]

# Documents no longer have a filepath to retrieve
async def get_document_path(id: int):
    # Get Inserted Documents ID
    doc = await dm.get_document_by_id(id)
    return doc[2]

# Main Driver Function, should route what needs to occur
# on document upload.
#Take in a filepath and the filetype

@router.post("/upload")
async def on_upload(src_file:UploadFile, user_id:int):
    #Get File Name
    source = src_file.filename
    #Insert File Owner and File Name Into DB
    #await dm.insert_document(user_id,source)
    #Parse File
    content = await parser.get_document_content(src_file,src_file.content_type)
    #Chunk Document
    chunks =  parser.get_content_chunks(content)
    #Insert Chunks into DB
    await  insert_chunks(source,chunks)
    #Delete Temp File
    src_file.close()
