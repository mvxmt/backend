import ollama

class PromptManager():
    def __init__(self,model="llama3.2:3b"):
        self.model = model


    async def get_relevance(self,chunk:str, user_prompt:str):
        client = ollama.AsyncClient()
        relevance_primer = '\
You are are an expert objective grader. \
It is your job to grade the following \
chunk of text provided in accordance to its relevance to \
a provided prompt. You will grade on a \
binary scale, with 0 meaning not relevant \
and 1 meaning relevant \
The original prompt will be surrounded with \
the <PROMPT></PROMPT> tags and the chunk \
to be graded will be outline with the \
<CHUNK></CHUNK> tag. \
You will give the numerical grading corresponding to the \
criteria mentioned above and you will provdie \
justification as to why the numerical value was selected \
Your output will be in the following format: \n\
numerical grade,  justification\
you will not include any additional formatting in your response \
Your justification will be clear and concise and only consist of a single sentence. \
Your grading will be harsh, and if a chunk does not directly address \
the provided prompt it will receive a 0.\
'
        message={'role' : 'user', 'content' : f'{relevance_primer} <PROMPT>{user_prompt}</PROMPT><CHUNK>{chunk}</CHUNK>'}
        try:
            response = await client.chat(model=self.model,messages=[message])
        except ollama.ResponseError as e:
                print('Error:',e.error)

        relevance = response['message']['content']
        relevance = relevance.split(',')
        score = 0
        justification = ""

        if len(relevance) > 1:
            if relevance[0].isnumeric():
                score = int(relevance[0])
            if not relevance[1].isnumeric():
                justification = relevance[1]

        return score, justification

    async def check_for_hallucination(self,chunk):
        pass
    
    async def load_context(self,ctx:list,user_prompt:str):
        client = ollama.AsyncClient()
        primer = 'You are an expert in the subject matter contained between the <PROMPT></PROMPT> tag. \
The users original prompt will be contained within that same <PROMPT></PROMPT> tag. You are to expand and \
augmet your own answer by using the provided context contained within the <CONTEXT></CONTEXT> tags. \
You will ensure your answer takes into consideration the provided context when you answer the users prompt. \
When using the provided context your answer you will ignore everything but the "text" \
portion of each provided context source and you will not mention that you were using context.'
        message={'role' : 'user', 'content' : f'{primer}\n<CONTEXT>{ctx}</CONTEXT>\n<PROMPT>{user_prompt}</PROMPT>'}
        try:
            response = await client.chat(model=self.model,messages=[message])
        except ollama.ResponseError as e:
                print('Error:',e.error)
        return response['message']['content']

    async def raw_answer(self,prompt:str):
        client = ollama.AsyncClient()
        message={'role' : 'user', 'content' : prompt}
        try:
            response = await client.chat(model=self.model,messages=[message])
        except ollama.ResponseError as e:
                print('Error:',e.error)
        return response['message']['content']