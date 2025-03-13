from unstructured.partition.auto import partition
import unstructured.documents.elements as el
from chonkie import SemanticChunker

class Parser:
    """
    A class to retrieve documents and convert them into smaller chunks of text.

    Methods:
    get_document(path) -> str: Reads a document from a given file path and extracts its textual content.
    get_document_chunks(doc, chunk_size) -> list[str]: Splits the document text into smaller chunks of a specified size.
    """

    async def get_document_content(self, file, filetype:str):
        try:
            part = partition(file=file,content_type=filetype)
        except TypeError as e:
            print("PARSER ERROR: ",e)

        return " ".join(element.text for element in part if isinstance(element, el.NarrativeText))

    async def get_content_chunks(self, content: str, max_chunk_size: int = 200):
        """
        Splits a document's text into smaller chunks of a specified token size.
        Uses a semantic chunking approach to divide the text while preserving meaning.
        """
        chunker = SemanticChunker(chunk_size=max_chunk_size)
        chunks = chunker(content)
        
        return [chunk.text for chunk in chunks]
