import ollama
import numpy as np


class QueryManager:
    def __init__(self, embedding_model="nomic-embed-text"):
        self.embedding_model = embedding_model
        self.user_input = ""

    def set_user_prompt(self, user_input):
        self.user_input = user_input

    async def embed_user_prompt(self):
        async with ollama.AsyncClient() as client:
            embedding = await client.embed(
                model=self.embedding_model, input=f"search_query: {self.user_input}"
            )
            embedding_array = np.array(embedding["embeddings"])
        return embedding_array

    def get_document_chunk(self, conn, result):
        # result is a list of tuples

        # each tuple contains
        """
        index 0: id
        index 1: document_id
        index 2: chunk_text
        index 3: chunk_vector
        """

        chunk_list = [{"document_id": row[1], "chunk_text": row[2]} for row in result]
        return chunk_list
