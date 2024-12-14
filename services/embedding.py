import ollama
import numpy as np

class EmbedManager:
    def __init__(self, embedding_model='nomic-embed-text'):
        self.embedding_model = embedding_model
    
    async def embed(self,text):
        client = ollama.AsyncClient()
        embedding = await client.embed(
            model=self.embedding_model, 
            input=f"search_query: {text}"
        )
        embedding_array = np.array(embedding['embeddings'][0])
        return embedding_array
    
