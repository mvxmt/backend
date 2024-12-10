import os
import asyncio
import importlib.util
import sys
import psycopg

#Database Manager Paths
database_chunk_path = '/db/database_chunks.py'
database_doc_path = '/db/database_documents.py'
#Services Paths
embedding_path = '/services/embedding.py'
parser_path = '/services/parser.py'
context_path = '/services/context.py'

#Environment Variable
os.environ["OLLAMA_HOST"] = "http://localhost:11434"

def _import_module(module_name,path):
    try:
        spec = importlib.util.spec_from_file_location(module_name,path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        return getattr(module,module_name)
    except (ModuleNotFoundError, AttributeError) as e:
        print(f"Error importing {module_name}: {e}")
        return None
    
async def _get_db_connection():
    connection_parameters = {
        'dbname' : 'rag_data',
        'user' : 'postgres',
        'host' : 'localhost',
        'port' : '5432'
    }
    try:
        conn = await psycopg.connect(**connection_parameters)
        return conn
    except psycopg.Error as e:
        print(f"Error connecting to the database: {e}")
        return None

async def main():
    #Import Modules
    #Database
    DatabaseDocumentManager = _import_module("db_doc",database_doc_path)
    DatabaseChunkManager = _import_module("db_chunk",database_chunk_path)
    #Services
    Embedding = _import_module('embedding',embedding_path)
    Parser = _import_module('parser',parser_path)
    Context = _import_module('context',context_path)

    #Connect to Database
    conn = await _get_db_connection()
    if conn:
        em = Embedding()
        cm = DatabaseChunkManager(conn)
        ctx = Context()

        prompt = input("Please Enter a Prompt: ") #Replace with request to front end
        embed = em.embed(prompt)
        results = cm.get_related_chunks(embed)
        context = ctx.get_context(results)
        print(context) #Replace with answer_prompt from Prompt Manager

        await conn.close()

asyncio.run(main())
