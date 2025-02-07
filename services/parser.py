import os
from unstructured.partition.text import partition_text
from unstructured.partition.pdf import partition_pdf
from unstructured.partition.doc import partition_doc
from unstructured.partition.docx import partition_docx
from unstructured.partition.xml import partition_xml
import unstructured.documents.elements as el


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

        partition_fileType() -> Retrieves a list of element types
        """
        _, extension = os.path.splitext(path)
        match extension[1:]:
            case "txt":
                part = partition_text(filename=path)
                text_list = [element.text for element in part]
                doc = " ".join(text_list)
            case "pdf":
                """
                Elements that are not inherently text types are ignored.

                Note: unlike the "doc" case, some elements could not be used with
                str() in order to filter out non text-based elements. Instead it
                would crash. Further Testing is required.

                Supported Elements (concurrently):
                - Title
                - NarrativeText
                """

                part = partition_pdf(filename=path)

                textList = []

                for element in part:
                    if isinstance(element, el.Title):
                        textList.append(f"{element.text}.")
                    elif isinstance(element, el.NarrativeText):
                        textList.append(element.text)
                doc = " ".join([text for text in textList])

            case "doc":
                """
                Note: 
                - partition_doc requires libreoffice to convert the file into a .docx before 
                 partitioning.
                """
                part = partition_doc(filename=path)
                doc = "".join(
                    [str(element) for element in part]
                )  # str() ignores non text-based elements
            case "docx":
                part = partition_docx(filename=path)
                doc = "".join([str(element) for element in part])
            case "xml":
                doc = partition_xml(filenme=path)
        return doc

    def get_document_chunks(self, doc: str, chunk_size: int):
        """
        Takes in a doc (str) and chunk size (int), returns a list of text chunks of the
        specified size. Emphasizes complete sentences to retain context over exact chunk
        size.

        max_characters: int (default=500) The hard maximum size for a chunk. No chunk will
            exceed this number of characters. A single element that by itself exceeds this
            size will be divided into two or more chunks using text-splitting.
        new_after_n_chars: int (default=max_characters) The "soft" maximum size for a chunk.
            A chunk that already exceeds this number of characters will not be extended, even
            if the next element would fit without exceeding the specified hard maximum. This
            can be used in conjunction with max_characters to set a "preferred" size, like
            "I prefer chunks of around 1000 chars, but I'd rather have a chunk of 1500
            (max_characters) than resort to text-splitting"

        Main: Chunk a string of text or combine with get_document function.
        """

        # chunks = partition_text(
        #     filename=path,
        #     strategy="fast",
        #     chunking_strategy="basic",
        #     max_character=200,
        #     new_after_n_chars=chunk_size,
        # )

        # chunks = partition_pdf(
        #     filename=path,
        #     strategy="fast",
        #     chunking_strategy="basic",
        #     max_character=200,
        #     new_after_n_chars=chunk_size,
        # )

        # chunks = partition_doc(
        #     filename=path,
        #     strategy="fast",
        #     chunking_strategy="basic",
        #     max_character=200,
        #     new_after_n_chars=chunk_size,
        # )
        # chunks = partition_docx(
        #     filename=path,
        #     strategy="fast",
        #     chunking_strategy="basic",
        #     max_character=200,
        #     new_after_n_chars=chunk_size,
        # )
        # chunks = partition_xml(
        #     filename=path,
        #     strategy="fast",
        #     chunking_strategy="basic",
        #     xml_keep_tags=True,
        #     max_character=200,
        #     new_after_n_chars=chunk_size,
        # )
