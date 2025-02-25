import os


class Parser:
    """
    A class to retrieve and documents and convert them into smaller chunks of text.

    Methods:
    get_document(path) -> str: Retrieves a document from a filepath and returns a string.
    get_document_chunks(doc,chunk_size) -> str and int: Returns a list of text chunks.
    """

    def get_document(self, path: str):
        """
        Takes in a filepath (str) and returns a string of text.
        """
        _, extension = os.path.splitext(path)
        match extension[1:]:
            case "txt":
                with open(path, "r") as file:
                    doc = file.read()
            case "pdf":
                pass
            case "doc":
                pass
            case "docx":
                pass
            case "xml":
                pass
        return doc

    def get_document_chunks(self, doc: str, chunk_size: int):
        """
        Takes in a doc (str) and chunk size (int), returns a list of text chunks
        of the specified size. It replaces newlines with spaces to avoid unncessary
        line breaks. Emphasizes complete sentences to retain context over exact chunk size.
        """
        size = chunk_size
        chunks = []
        current_chunk = []
        text = doc.replace(
            "\n", " "
        )  # Replaces newlines with spaces to avoid unncessary line breaks
        j = 0
        for i in range(len(text)):
            current_chunk.append(text[i])  # Add letter to current chunk
            j += 1  # Additonal Counter to keep track of chunk size
            # Continue the loop until the end of sentence is reached
            if j == size:
                if text[i] == ".":
                    current_chunk = "".join(current_chunk)
                    chunks.append(current_chunk)
                    current_chunk = []
                    j = 0
                else:
                    j -= 1
        return chunks
