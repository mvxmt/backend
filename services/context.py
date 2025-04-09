from .crypto import CryptographyManager
from pydantic import BaseModel

class IndexableBaseModel(BaseModel):
    """Allows a BaseModel to return its fields by string variable indexing"""
    def __getitem__(self, item):
        return getattr(self, item)

class RAGContext(IndexableBaseModel):
    id: int
    source: str
    text: str

class ContextManager:
    def __init__(self, crypto: CryptographyManager):
        self.crypto = crypto

    def get_context(self, chunks: BaseModel):
        """
        Takes in pydantic model consisting of:
        id: int
        source: str
        test: str
        distance: str
        """
        chunk_list = [
            RAGContext(
                id=chunk.id, source=chunk.source, text=self.crypto.decrypt_string(chunk.text)
            )
            for chunk in chunks
        ]
        return chunk_list
