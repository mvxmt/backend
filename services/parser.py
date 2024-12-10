class Parser:
    def get_document(self,path):
        with open(path,"r") as file:
            doc = file.read()
        return doc

    def get_document_chunks(self, doc :str,chunk_size: int):
        size = chunk_size
        chunks = []
        current_chunk = []
        text = doc.replace('\n',' ')
        j=0

        for i in range(len(text)):
            current_chunk.append(text[i])
            j += 1
            if j == size:
                if text[i] == '.':
                    current_chunk = ''.join(current_chunk)
                    chunks.append(current_chunk )
                    current_chunk  = []
                    j = 0
                else:
                    j -=1
        return chunks