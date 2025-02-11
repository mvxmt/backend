import os
from unstructured.partition.text import partition_text
from unstructured.partition.pdf import partition_pdf
from unstructured.partition.doc import partition_doc
from unstructured.partition.docx import partition_docx
import unstructured.documents.elements as el
from chonkie import SemanticChunker


class Parser:
    """
    A class to retrieve and documents and convert them into smaller chunks of text.

    Methods:
    get_document(path) -> str: Retrieves a document from a filepath and returns a tuple
                                including the doc text (str) and a list of titles (str)
    get_document_chunks(doc,chunk_size) -> str and int: Returns a list of text chunks.
    """

    def get_document(self, path: str):
        """
        Takes in a filepath (str) and returns a tuple of a string of document text and a
         list of title strings (str, [str])

        partition_fileType() -> List of elements

        Elements that are not inherently text types are ignored.

        Supported Elements (concurrently):
        - Title
        - NarrativeText
        """
        _, extension = os.path.splitext(path)
        match extension[1:]:
            case "txt":
                part = partition_text(filename=path)

            case "pdf":
                part = partition_pdf(filename=path)

            case "doc":
                """
                .doc requires libreoffice to convert the file into a .docx before parsing,
                dont forget to install libreoffice on server
                """
                part = partition_doc(filename=path)

            case "docx":
                part = partition_docx(filename=path)
            case "xml":
                pass
            case _:
                raise ValueError("Unsupported file type")

        text_list, title_list = [], []
        for element in part:
            if isinstance(element, el.Title):
                title_list.append(element.text)
            elif isinstance(element, el.NarrativeText):
                text_list.append(element.text)

        return (" ".join(text_list), title_list)

    def get_document_chunks(self, doc: str, max_chunk_size: int):
        """
        Takes in a doc (str) and chunk size (int), returns a list of text chunks of the
        specified size (in tokens)
        """
        chunker = SemanticChunker(chunk_size=max_chunk_size)
        chunks = chunker(doc)

        return chunks
