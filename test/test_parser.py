import unittest
from services.parser import Parser

class TestParser(unittest.TestCase):
    def set_up(self):
        self.parser = Parser()

    # File Types
    def test_get_document_txt(self):
      result = self.parser.get_document("/content/sample_data/sample(tdd).txt")
      self.assertIsInstance(result, str)
      self.assertTrue(len(result) > 0)

    def test_get_document_pdf(self):
      result = self.parser.get_document("/content/sample_data/sample(tdd).pdf")
      self.assertIsInstance(result, str)
      self.assertTrue(len(result) > 0)

    def test_get_document_doc(self):
      result = self.parser.get_document("/content/sample_data/sample(tdd).doc")
      self.assertIsInstance(result, str)
      self.assertTrue(len(result) > 0)

    def test_get_document_docx(self):
      result = self.parser.get_document("/content/sample_data/sample(tdd).docx")
      self.assertIsInstance(result, str)
      self.assertTrue(len(result) > 0)

    def test_get_document_unsupported_file(self):
      with self.assertRaises(ValueError):
        self.parser.get_document("/content/sample_data/sample(tdd).odt")

    # Chunking
    def test_get_document_chunks(self):
      document_text = self.parser.get_document("/content/sample_data/sample(tdd).txt")
      chunks = self.parser.get_document_chunks(document_text, 100)
      self.assertIsInstance(chunks, list)

      for chunk in chunks:
        self.assertIsInstance(chunk, str)

    def test_get_chunks_max_chunk_size_is_int(self):
        document_text = "Some text to chunk"
        with self.assertRaises(TypeError):
            self.parser.get_document_chunks(document_text, "invalid_size")

unittest.main(argv=[''], verbosity=2, exit=False)
