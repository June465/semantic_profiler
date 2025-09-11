import unittest
from typing import List
from backend.core.text_splitter import clean_text, split_text_into_chunks

class TestTextSplitter(unittest.TestCase):

    def setUp(self):
        """Set up common test data."""
        self.raw_text_with_noise = """
        John Doe
        Software Engineer

        Experience:
        Senior Developer at Tech Solutions Inc. (2020-Present)
        - Led development of new features.

        Junior Dev at XYZ Corp (2018-2020)
        - Assisted in various projects.
        Page 1 of 2

        Education:
        B.S. Computer Science - University of ABC (2014-2018)

        Skills:
        Python, Java, AWS, Docker, Kubernetes

        More info on page 2.
        Certifications: AWS Certified Developer.
        Projects: Built an e-commerce platform.
        1 | 2
        Final notes.
        """

        self.expected_cleaned_text_sample = "John Doe Software Engineer Experience: Senior Developer at Tech Solutions Inc. (2020-Present) - Led development of new features. Junior Dev at XYZ Corp (2018-2020) - Assisted in various projects. Education: B.S. Computer Science - University of ABC (2014-2018) Skills: Python, Java, AWS, Docker, Kubernetes More info on page 2. Certifications: AWS Certified Developer. Projects: Built an e-commerce platform. Final notes."

        self.cleaned_long_text = clean_text("A B C D E F G H I J K L M N O P Q R S T U V W X Y Z " * 5)
        self.cleaned_sentence_text = clean_text("This is a very long sentence that needs to be chunked with a large overlap.")


    def test_clean_text_basic(self):
        """Test basic whitespace normalization and strip."""
        text = "  Hello \t World!  \n  This is a test.   \n\n  "
        cleaned = clean_text(text)
        self.assertEqual(cleaned, "Hello World! This is a test.")

    def test_clean_text_multiple_newlines(self):
        """Test reducing multiple newlines (now all collapsed to single spaces)."""
        text = "Line 1\n\n\nLine 2\n\nLine 3"
        cleaned = clean_text(text)
        self.assertEqual(cleaned, "Line 1 Line 2 Line 3")

    def test_clean_text_page_numbers(self):
        """Test removal of page number patterns."""
        text = "Content here. Page 1 of 3. More content. 2 | 3. Last page 3/3."
        cleaned = clean_text(text)
        self.assertNotIn("Page 1 of 3", cleaned)
        self.assertNotIn("2 | 3", cleaned)
        self.assertNotIn("3/3", cleaned)
        self.assertEqual(cleaned, "Content here. More content. Last page.")

    def test_clean_text_with_noise_patterns(self):
        """Test cleaning with a mix of noise patterns."""
        cleaned = clean_text(self.raw_text_with_noise)
        self.assertEqual(cleaned, self.expected_cleaned_text_sample)
        self.assertFalse("  " in cleaned) # No double spaces
        self.assertFalse("\n" in cleaned) # No newlines left
        self.assertGreater(len(cleaned), 100) # Ensure content remains

    def test_clean_text_empty_input(self):
        """Test cleaning an empty string."""
        self.assertEqual(clean_text(""), "")
        self.assertEqual(clean_text("   "), "")

    def test_clean_text_non_string_input(self):
        """Test clean_text with non-string input."""
        self.assertEqual(clean_text(None), "")
        self.assertEqual(clean_text(123), "")
        self.assertEqual(clean_text(['abc']), "")


    def test_split_text_into_chunks_basic(self):
        """Test splitting a simple text into chunks."""
        text = self.cleaned_long_text
        chunk_size = 20
        chunk_overlap = 5
        chunks = split_text_into_chunks(text, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        
        self.assertGreater(len(chunks), 1)
        self.assertLessEqual(len(chunks[0]), chunk_size + chunk_overlap) # Allow for slight overshoot

        if len(chunks) > 1:
            overlap_segment = "I J"
            self.assertIn(overlap_segment, chunks[0], f"'{overlap_segment}' not found in chunk 0: '{chunks[0]}'")
            self.assertIn(overlap_segment, chunks[1], f"'{overlap_segment}' not found in chunk 1: '{chunks[1]}'")
        else:
            pass

    def test_split_text_into_chunks_no_overlap(self):
        """Test splitting with zero overlap."""
        text = "abcdefghijklmnopqrstuvwxyz" * 2 # 52 chars
        chunks = split_text_into_chunks(text, chunk_size=10, chunk_overlap=0)
        self.assertEqual(len(chunks), 6) # 5 full chunks of 10, plus 1 chunk of 2.
        self.assertEqual(chunks[0], "abcdefghij")
        self.assertEqual(chunks[1], "klmnopqrst")
        self.assertNotIn("abcdefghij", chunks[1]) # Ensure no overlap

    def test_split_text_into_chunks_long_overlap(self):
        """Test splitting with a significant overlap."""
        text = self.cleaned_sentence_text
        chunk_size = 30
        chunk_overlap = 15
        chunks = split_text_into_chunks(text, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        self.assertGreater(len(chunks), 1)
        self.assertLessEqual(len(chunks[0]), chunk_size + chunk_overlap) # Allow for slight overshoot

        if len(chunks) > 1:
            expected_overlap_segment = "sentence"
            self.assertIn(expected_overlap_segment, chunks[0], f"'{expected_overlap_segment}' not in chunk 0: '{chunks[0]}'")
            self.assertIn(expected_overlap_segment, chunks[1], f"'{expected_overlap_segment}' not in chunk 1: '{chunks[1]}'")
        else:
            pass

    def test_split_text_into_chunks_empty_input(self):
        """Test chunking an empty string."""
        self.assertEqual(split_text_into_chunks(""), [])
        self.assertEqual(split_text_into_chunks("   \n\t  "), [])

    def test_split_text_into_chunks_non_string_input(self):
        """Test chunking with non-string input."""
        self.assertEqual(split_text_into_chunks(None), [])
        self.assertEqual(split_text_into_chunks(123), [])
        self.assertEqual(split_text_into_chunks(['abc']), [])

    def test_split_text_into_chunks_small_text(self):
        """Test text smaller than chunk_size."""
        text = "This is a short text."
        chunks = split_text_into_chunks(text, chunk_size=100, chunk_overlap=20)
        self.assertEqual(len(chunks), 1)
        self.assertEqual(chunks[0], text)


if __name__ == '__main__':
    unittest.main()