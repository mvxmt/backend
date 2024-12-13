import os
import asyncio

class UploadManager:
    def __init__(self,conn,db_document_manager,db_chunk_manager,parser):
        self.conn = conn
        self.dm = db_document_manager
        self.cm = db_chunk_manager
        self.parser = parser
        self.path = os.getenv("DATA_DIR")

    async def save_to_disk(self,document,filepath:str):
        extension = filepath.split(".")
        match extension[1]:
            case'txt':
                with open(filepath, "w") as file:
                    file.write(document)
            case 'pdf':
                with open(filepath, "wb") as file:
                    file.write(document)
            case 'xml':
                with open(filepath, "w", encoding='utf-8') as file:
                    file.write(document)

    async def insert_uploaded_document(self,filename:str,user_id:int):
        path = os.getenv("DATA_DIR")
        filepath = str(path + filename)
        self.dm.insert_document(user_id,filepath)

    async def chunk_uploaded_document(self,filename:str,chunk_size:int):
        filepath = str(self.path + filename)
        doc = self.parser.get_document(filepath)
        chunks = self.parser.get_document_chunks(doc,chunk_size)
        return chunks
    
    async def insert_chunks(self,document_id:int, chunks:list):
        for chunk_text in chunks:
            chunk_vector = self.em.embed(chunk_text)
            self.cm.insert(document_id,chunk_text,chunk_vector)

    async def get_document_id(self,filename:str):
        #Get Inserted Documents ID
        doc = self.dm.get_document_by_filename(filename)
        return doc[0]
    
    async def get_document_path(self,id:int):
        #Get Inserted Documents ID
        doc = self.dm.get_document_by_id(id)
        return doc[2]

