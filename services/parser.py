import os
from unstructured.partition.text import partition_text
from unstructured.partition.pdf import partition_pdf
from unstructured.partition.doc import partition_doc
from unstructured.partition.docx import partition_docx
from unstructured.partition.xml import partition_xml


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

        Note: Pdf files will need a proper way of formatting its text
        """
        _, extension = os.path.splitext(path)
        match extension[1:]:
            case "txt":
                """
                partition_text() -> NarrativeText element
                """
                doc = partition_text(filename=path)[0]
            case "pdf":
                """
                partition_pdf() -> Title and NarativeText elements
                """
                doc = partition_pdf(filename=path)
            case "doc":
                """
                .doc requires libreoffice to convert the file into a .docx before parsing,
                dont forget to install libreoffice on server

                partition_doc() -> ListItem, Text, NarrativeText, and Table elements
                """
                part = partition_doc(filename=path)
                doc = "".join(
                    [str(element) for element in part]
                )  # ignores elements that arent explicitly text elements.
            case "docx":
                doc = partition_docx(filename=path)
            case "xml":
                doc = partition_xml(filenme=path)
        return doc

    def get_document_chunks(self, path: str, chunk_size: int):
        """
        Takes in a filepath (str) and returns chunk elements.

        max_characters: int (default=500) The hard maximum size for a chunk. No chunk will
            exceed this number of characters. A single element that by itself exceeds this
            size will be divided into two or more chunks using text-splitting.
        new_after_n_chars: int (default=max_characters) The "soft" maximum size for a chunk.
            A chunk that already exceeds this number of characters will not be extended, even
            if the next element would fit without exceeding the specified hard maximum. This
            can be used in conjunction with max_characters to set a "preferred" size, like
            "I prefer chunks of around 1000 chars, but I'd rather have a chunk of 1500
            (max_characters) than resort to text-splitting"

        Note: pdf will need a proper way to format its text for chunking
        """
        if not os.path.exists(path):
            raise FileNotFoundError("File not found")

        _, extension = os.path.splitext(path)
        match extension[1:]:
            case "txt":
                chunks = partition_text(
                    filename=path,
                    strategy="fast",
                    chunking_strategy="basic",
                    max_character=200,
                    new_after_n_chars=chunk_size,
                )
            case "pdf":
                """
                Note: Pdf text needs to be cleaned for chunking
                """
                chunks = partition_pdf(
                    filename=path,
                    strategy="fast",
                    chunking_strategy="basic",
                    max_character=200,
                    new_after_n_chars=chunk_size,
                )
            case "doc":
                """
                .doc requires libreoffice to convert the file into a .docx before parsing,
                dont forget to install libreoffice on server
                """
                chunks = partition_doc(
                    filename=path,
                    strategy="fast",
                    chunking_strategy="basic",
                    max_character=200,
                    new_after_n_chars=chunk_size,
                )
            case "docx":
                chunks = partition_docx(
                    filename=path,
                    strategy="fast",
                    chunking_strategy="basic",
                    max_character=200,
                    new_after_n_chars=chunk_size,
                )
            case "xml":
                chunks = partition_xml(
                    filename=path,
                    strategy="fast",
                    chunking_strategy="basic",
                    xml_keep_tags=True,
                    max_character=200,
                    new_after_n_chars=chunk_size,
                )
            case _:
                raise ValueError("Unsupported file type")
        return chunks
