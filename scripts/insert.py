import os
import asyncio
import importlib.util
import sys
import psycopg
from dotenv import load_dotenv


async def _get_db_connection():
    connection_parameters = {
        "dbname": "rag_data",
        "user": "postgres",
        "host": "localhost",
        "port": "5432",
    }
    try:
        conn = await psycopg.AsyncConnection.connect(**connection_parameters)
        return conn
    except psycopg.Error as e:
        print(f"Error connecting to the database: {e}")
        return None


def _import_module(module_name, path):
    try:
        spec = importlib.util.spec_from_file_location(module_name, path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        return module
        # return getattr(module,module_name)
    except (ModuleNotFoundError, AttributeError) as e:
        print(f"Error importing {module_name}: {e}")
        return None


async def main():
    load_dotenv(".env.example", override=True)
    path = os.getenv("LOCAL_PATH")
    # Database Manager Paths
    database_chunk_path = str(path + "/db/database_chunks.py")
    database_doc_path = str(path + "/db/database_documents.py")
    # Services Path
    embedding_path = str(path + "/services/embedding.py")
    parser_path = str(path + "/services/parser.py")
    # context_path = '/services/context.py'

    # Import Modules
    # Database
    DatabaseDocumentManager_Module = _import_module(
        "database_documents", database_doc_path
    )
    DatabaseChunkManager_Module = _import_module("database_chunks", database_chunk_path)
    # Services
    Embedding_Module = _import_module("embedding", embedding_path)
    Parser_Module = _import_module("parser", parser_path)
    # Context = _import_module('context',context_path)

    opt = ""
    # Get Document Chunks
    path = os.getenv("DATA_DIR")
    filename = "demo_text.txt"
    filepath = str(path + filename)
    parser = Parser_Module.Parser()
    if os.path.exists(filepath):
        print("Do you want to chunk the following documet:{filename}?")
        opt = input("Y/N\n")
        if opt == "y":
            doc = parser.get_document(filepath)
            chunks = parser.get_document_chunks(doc, 100)
    else:
        print("Error: Unable to find File")
        return

    # Connect to Database
    conn = await _get_db_connection()
    if conn:
        em = Embedding_Module.EmbedManager()
        dm = DatabaseDocumentManager_Module.DatabaseDocumentManager(conn)
        cm = DatabaseChunkManager_Module.DatabaseChunkManager(conn)
        # ctx = Context()

    # Insert Doc
    path = os.getenv("DATA_DIR")
    filename = "demo_text.txt"
    filepath = str(path + filename)

    if os.path.exists(filepath):
        print(f"Do you want to insert the following documet:{filename}")
        opt = input("Y/N\n")
        if opt == "y":
            await dm.insert_document(1, filepath)
            # Get Inserted Documents ID
            doc = await dm.get_document_by_filename(filename)
            doc_id = doc[0]
    else:
        print("Error: Unable to find File")
        return

    if len(chunks) > 0:
        print(f"Do you want to insert {len(chunks)} chunks into database Y/N")
        opt = input("Y/N\n")
        if opt == "y":
            # Insert Chunks
            for chunk_text in chunks:
                chunk_vector = await em.embed(chunk_text)
                await cm.insert(doc_id, chunk_text, chunk_vector)
    else:
        print("Error: No chunks to insert")
        return

    await conn.close()


asyncio.run(main())
