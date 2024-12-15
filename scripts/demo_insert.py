import sys

# sys hacks to get imports to work
sys.path.append("./")

import os
import asyncio
from tqdm import tqdm
from dotenv import load_dotenv

from db.database_documents import DatabaseDocumentManager
from db.database_chunks import DatabaseChunkManager
from db.client import get_database_session
from services.embedding import EmbedManager
from services.parser import Parser

load_dotenv()

async def main():
    opt=""
    #Get Document Chunks
    path = os.environ.get("LOCAL_PATH")
    filename = "demo_text.txt"
    filepath = str(path + filename)
    parser = Parser()

    if os.path.exists(filepath):
        print(f"Do you want to chunk the following document: {filename}?")
        opt = input("Y/N\n")
        if opt=="y":
            doc = parser.get_document(filepath)
            chunks = parser.get_document_chunks(doc,100)
    else:
        print("Error: Unable to find File")
        return

    #Connect to Database
    async for conn in get_database_session():
        em = EmbedManager()
        dm = DatabaseDocumentManager(conn)
        cm = DatabaseChunkManager(conn)

        #Insert Doc
        path = os.getenv("DATA_DIR")
        filename = "demo_text.txt"
        filepath = str(path + filename)
        
        if os.path.exists(filepath):
            print(f"Do you want to insert the following document: {filename}")
            opt = input("Y/N\n")
            if opt=="y":
                await dm.insert_document(1,filepath)
            #Get Inserted Documents ID
            doc = await dm.get_document_by_filename(filename)
            doc_id = doc[0][0]
        else:
            print("Error: Unable to find File")
            return

        if len(chunks) > 0:
            print(f"Do you want to insert {len(chunks)} chunks into database Y/N")
            opt = input("Y/N\n")
            if opt=="y":
                #Insert Chunks
                for chunk_text in tqdm(chunks):
                    chunk_embed = await em.embed(chunk_text)
                    if len(chunk_embed) > 0:
                        await cm.insert_chunk(doc_id,chunk_text,chunk_embed)
        else:
            print('Error: No chunks to insert')
            return
        
        print("Insertion Complete")

asyncio.run(main())