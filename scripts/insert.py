import os
from routing import _import_module
from routing import _get_db_connection

async def main():
    #Import Modules
    database_chunk_path = '/db/database_chunks.py'
    database_doc_path = '/db/database_documents.py'

    embedding_path = '/services/embedding.py'
    parser_path = '/services/parser.py'
    context_path = '/services/context.py'

    DatabaseDocumentManager = _import_module("db_doc",database_doc_path)
    DatabaseChunkManager = _import_module("db_chunk",database_chunk_path)


    Embedding = _import_module('embedding',embedding_path)
    Parser = _import_module('parser',parser_path)
    Context = _import_module('context',context_path)

    #Get Document Chunks
    path = os.getenv("DATA_DIR")
    filename = "demo_text.txt"
    filepath = str(path + filename)
    parser = Parser()
    doc = parser.get_document(filepath)
    chunks = parser.get_document_chunks(doc,100)

    #Connect to Database
    conn = await _get_db_connection()
    if conn:
        em = Embedding()
        dm = DatabaseDocumentManager(conn)
        cm = DatabaseChunkManager(conn)
        ctx = Context()

    #Insert Doc
    path = os.getenv("DATA_DIR")
    filename = "demo_text.txt"
    filepath = str(path + filename)
    dm.insert_document(1,filepath)
    #Get Inserted Documents ID
    doc = dm.get_document_by_filename(filename)
    doc_id = doc[0]

    #Insert Chunks
    for chunk_text in chunks:
        chunk_vector = em.embed(chunk_text)
        cm.insert(doc_id,chunk_text,chunk_vector)

