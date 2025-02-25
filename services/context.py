from .crypto import CryptographyManager
from pydantic import BaseModel


class RAGContext(BaseModel):
    id: int
    source: int
    text: str


class ContextManager:
    def __init__(self, crypto: CryptographyManager):
        self.crypto = crypto

    def get_context(self, result: tuple):
        # each tuple contains
        """
        index 0: id
        index 1: document_id
        index 2: chunk_text
        index 3: chunk_vector
        """
        chunk_list = [
            RAGContext(
                id=row[0], source=row[1], text=self.crypto.encrypt_string(row[2])
            )
            for row in result
        ]
        return chunk_list
