import ollama

class QueryManager:
    def __init__(self, embedding_model='nomic-embed-text'):
        self.embedding_model = embedding_model
    
    def get_user_prompt(self):
        return input("Send a message: ")
    
    def embed_user_prompt(self, prompt):
        embedding = ollama.embed(model=self.embedding_model, input=f"search_query: {prompt}")
        return embedding['embeddings']
    
    def query_database(self, conn, embedding):
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT chunk_vector
                FROM document_data.chunks
                ORDER BY 1 - (chunk_vector <=> %s::vector) DESC
                LIMIT 1;
                """,
                (embedding,),
            )
            result = cur.fetchone()
            return result
    
    def get_document_chunk(self, conn, embedding):
        db_results = self.query_database(conn, embedding)
        chunk_vector = db_results[0] 
        
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT document_id, chunk_text 
                FROM document_data.chunks 
                WHERE chunk_vector = %s;
                """,
                (chunk_vector,),  
            )
            result = cur.fetchone()
            dictionary = {'document_id': result[0], 'chunk_text': result[1]}
            return dictionary
           