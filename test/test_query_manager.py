import unittest
from query_manager import QueryManager

"""
index 0: id 
index 1: document_id
index 2: chunk_text
index 3: chunk_vector
"""


class TestQueryManager(unittest.TestCase):
    def test_get_user_prompt(self):
        expected_result = "I don't know"

        qm = QueryManager()
        qm.get_user_prompt("I don't know")

        self.assertIsEqual(qm.user_input, expected_result)

    def test_embed_user_prompt(self):
        import numpy as np
        import ollama

        embedding = ollama.embed(
            model=self.embedding_model, input="search_query: testing the embedding"
        )
        expected_embedding = np.array(embedding["embeddings"])

        qm = QueryManager()
        qm.get_user_prompt("testing the embedding")
        test_embedding = qm.embed_user_prompt()

        self.assertIsInstance(test_embedding, np.ndarray)
        self.assertEqual(test_embedding, expected_embedding)

    def test_get_document_chunk(self):
        # Simulated results
        result = [
            (1, 1, "the sky is blue", [0.1, 0.2, 0.3]),
            (2, 2, "hello there how are you doing?", [0.3, 0.4, 0.5]),
            (3, 3, "the quick brown fox", [0.2, 0.3, 0.4, 0.6])(
                4, 4, "python is a myth", [0.04, 0.03, 0.54]
            ),
        ]

        # Expected Output
        expected_output = [
            {"document_id": 1, "chunk_text": "the sky is blue"},
            {"document_id": 2, "chunk_text": "hello there how are you doing?"},
            {"document_id": 3, "chunk_text": "the quick brown fox"},
            {"document_id": 4, "chunk_text": "python is a myth"},
        ]

        qm = QueryManager()
        result_output = qm.get_document_chunk(None, result)

        self.assertEqual(result_output, expected_output)


if __name__ == "__main__":
    unittest.main()
