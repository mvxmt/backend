from original_query_manager import query_manager
from database_manager import database_manager


q_manager = query_manager()
db_manager = database_manager()

conn = db_manager.db_connect()

if not conn:
    print("Failed to connect to the database.")

else:
    with conn:
            # Step 1: Get the user prompt
            user_prompt = q_manager.get_user_prompt()

            # Step 2: Embed the user prompt 
            embedding = q_manager.embed_user_prompt(user_prompt)
            
            # Step 3: Query the Database
            db_results = q_manager.query_database(conn, embedding)

            # Step 4: Get the document chunk info
            document_chunk = q_manager.get_document_chunk(conn, db_results)
            print(document_chunk)