import os

from psycopg import AsyncConnection
from db.database_documents import DatabaseDocumentManager
from db.database_chunks import DatabaseChunkManager
from .crypto import CryptographyManager
from .embedding import EmbedManager
from .parser import Parser
import ulid
import pathlib

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

    async def insert_uploaded_document(self, src_file: str, user_id: int):
        data_dir = pathlib.Path(self.path)
        p = data_dir / src_file

        if p.exists() and p.is_file():
            size = len(p.read_bytes())
            self.dm.insert_document(user_id, str(p), size, src_file)

    async def chunk_uploaded_document(self, filename: str, chunk_size: int):
        filepath = str(self.path + filename)
        doc = self.parser.get_document(filepath)
        chunks = self.parser.get_document_chunks(doc, chunk_size)
        return chunks

    async def insert_chunks(self, document_id: int, chunks: list[str]):
        for chunk_text in chunks:
            chunk_vector = await self.em.embed(chunk_text)
            chunk_ciphertext = self.crypto.encrypt_bytes(chunk_text.encode())
            await self.cm.insert_chunk(document_id, chunk_ciphertext.decode(), chunk_vector)

    async def get_document_id(self, filename: str):
        # Get Inserted Documents ID
        doc = await self.dm.get_document_by_filename(filename)
        return doc[0]

    async def get_document_path(self, id: int):
        # Get Inserted Documents ID
        doc = await self.dm.get_document_by_id(id)
        return doc[2]
