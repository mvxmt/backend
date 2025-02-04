import ollama
import numpy as np

class PromptManager():
    def __init__(self,model="llama 3.2:3b"):
        self.model = model

    async def embed(self, text):
        client = ollama.AsyncClient()
        embedding = await client.embed(
            model=self.embedding_model, input=f"search_query: {text}"
        )
        embedding_array = np.array(embedding["embeddings"][0])
        return embedding_array


    async def get_relevance(self,chunk, user_prompt):
        client = ollama.AsyncClient()
        relevance_primer = """
                            You are are an objective grader.
                            It is your job to ensure that the 
                            chunk of text provided is relevant to 
                            a users prompt. You will grade on a 
                            scale of 0-5, with the numerical values 
                            having the corresponding 
                            definitions outlined in JSON: \n
                                {
                                \n
                                0: Non-relevant,\n
                                1: Somewhat Relevant,\n
                                2: Semi Relevant,\n
                                3: Relevant,\n
                                4: Very Relevant,\n
                                5: Highly Relevant
                                \n},\n
                            The original prompt will be surrounded with 
                            the <PROMPT></PROMPT> tags and the chunk 
                            to be graded will be outline with the 
                            <CHUNK></CHUNK> tag.
                            Your output will be in JSON format outlined like so:\n
                            { numerical grade: chunk }\n
                            """
        message={'role' : 'user', 'content' : f'{relevance_primer}\
                 <PROMPT>{user_prompt}</PROMPT><CHUNK>{chunk}</CHUNK>'}
        relevance = await client.chat(model=self.model,messages=[message])
        return relevance

    async def check_for_hallucination(self,chunk):
        pass
    
    async def load_context(self,ctx):
        pass

    async def display_answer(self):
        pass