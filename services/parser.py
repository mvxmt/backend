import os
from unstructured.partition.text import partition_text
from unstructured.partition.pdf import partition_pdf
from unstructured.partition.doc import partition_doc
from unstructured.partition.docx import partition_docx
import unstructured.documents.elements as el
from chonkie import SemanticChunker



class Parser:
    """
    A class to retrieve documents and convert them into smaller chunks of text.

    Methods:
    get_document(path) -> str: Reads a document from a given file path and extracts its textual content.
    get_document_chunks(doc, chunk_size) -> list[str]: Splits the document text into smaller chunks of a specified size.
    """

    def get_document(self, path: str):
        """
        Reads a document from a file and returns its textual content as a string.
        Uses format-specific partitioning functions to extract text elements.
        Only textual elements are retained.
        """
        _, extension = os.path.splitext(path)
        match extension[1:]:
            case "txt":
                part = partition_text(filename=path)

            case "pdf":
                part = partition_pdf(filename=path)

            case "doc":
                """
                .doc files require LibreOffice to be installed for conversion to .docx before processing.
                Ensure LibreOffice is available on the system
                """
                part = partition_doc(filename=path)

            case "docx":
                part = partition_docx(filename=path)
            
            case _:
                raise ValueError("Unsupported file type")

        return " ".join(element.text for element in part if isinstance(element, el.NarrativeText))

    def get_document_chunks(self, doc: str, max_chunk_size: int):
        """
        Splits a document's text into smaller chunks of a specified token size.
        Uses a semantic chunking approach to divide the text while preserving meaning.
        """
        chunker = SemanticChunker(chunk_size=max_chunk_size)
        chunks = chunker(doc)
        
        return [chunk.text for chunk in chunks]
