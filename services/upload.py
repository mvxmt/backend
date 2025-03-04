import os
import pathlib

from psycopg import AsyncConnection

from db.database_chunks import DatabaseChunkManager
from db.database_documents import DatabaseDocumentManager

from .crypto import CryptographyManager
from .embedding import EmbedManager
from .parser import Parser


class UploadManager:
    def __init__(
        self,
        conn: AsyncConnection,
        db_document_manager: DatabaseDocumentManager,
        db_chunk_manager: DatabaseChunkManager,
        embed_manager: EmbedManager,
        crypto: CryptographyManager,
        parser: Parser,
    ):
        self.conn = conn
        self.dm = db_document_manager
        self.cm = db_chunk_manager
        self.parser = parser
        self.crypto = crypto
        self.em = embed_manager
        self.path = os.getenv("DATA_DIR")

    # Docuemnts no longer needed to be saved to disk
    # local copy gets ingested and then deleted.
    async def save_to_disk(self, document, filepath: str):
        _, extension = os.path.splitext(filepath)
        match extension[1:]:
            case "txt":
                with open(filepath, "w") as file:
                    file.write(document)
            case "pdf":
                with open(filepath, "wb") as file:
                    file.write(document)
            case "xml":
                with open(filepath, "w", encoding="utf-8") as file:
                    file.write(document)

    # Documents no longer need to be uploaded,
    # they need to be fed into the parser manager
    async def insert_uploaded_document(self, src_file: str, user_id: int):
        data_dir = pathlib.Path(self.path)
        p = data_dir / src_file

        if p.exists() and p.is_file():
            await self.dm.insert_document(user_id, src_file)

    async def chunk_uploaded_document(self, filename: str, chunk_size: int):
        filepath = str(self.path + filename)
        doc = self.parser.get_document(filepath)
        chunks = self.parser.get_document_chunks(doc, chunk_size)
        return chunks

    async def insert_chunks(self, document_id: int, chunks: list[str]):
        for chunk_text in chunks:
            chunk_vector = await self.em.embed(chunk_text)
            chunk_ciphertext = self.crypto.encrypt_bytes(chunk_text.encode())
            await self.cm.insert_chunk(
                document_id, chunk_ciphertext.decode(), chunk_vector
            )

    # Documents should still be assigned an ID to keep track of
    # the source document and organize chunks
    async def get_document_id(self, filename: str):
        # Get Inserted Documents ID
        doc = await self.dm.get_document_by_filename(filename)
        return doc[0]

    # Documents no longer have a filepath to retrieve
    async def get_document_path(self, id: int):
        # Get Inserted Documents ID
        doc = await self.dm.get_document_by_id(id)
        return doc[2]

    # Main Driver Function, should route what needs to occur
    # on document upload.
    async def on_upload(self):
        pass
