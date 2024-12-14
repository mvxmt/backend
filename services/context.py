class ContextManager:
    def get_context(self, conn, result):
        # each tuple contains
        """
        index 0: id
        index 1: document_id
        index 2: chunk_text
        index 3: chunk_vector
        """
        chunk_list = [{"document_id": row[1], "chunk_text": row[2]} for row in result]
        return chunk_list
