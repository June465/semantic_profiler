import re
from typing import List
from langchain.text_splitter import RecursiveCharacterTextSplitter

def clean_text(text: str) -> str:
    """
    Performs thorough cleaning of extracted text from resumes.
    Aims to normalize whitespace, remove common noise, and create a single, flattened string.

    Args:
        text (str): The raw text extracted from a resume.

    Returns:
        str: The thoroughly cleaned, flattened text.
    """
    if not isinstance(text, str):
        return ""

    # Ensure input is string for regex operations
    cleaned_text = str(text)

    # Step 1: Remove common resume noise patterns with empty string replacement.
    page_number_patterns = r'\bPage\s+\d+\s+of\s+\d+\b|\b\d+\s*\|\s*\d+\b|\b\d+/\d+\b'
    cleaned_text = re.sub(page_number_patterns, '', cleaned_text, flags=re.IGNORECASE)

    # Step 2: Normalize all whitespace (including newlines, tabs, multiple spaces) to a single space.
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text)

    # Step 3: Clean up punctuation artifacts.
    # 3a. Remove any space that appears directly before a punctuation mark.
    # Example: "word . " -> "word."
    cleaned_text = re.sub(r'\s+([.,;!?:])', r'\1', cleaned_text)

    # 3b. Replace multiple consecutive punctuation marks with a single one.
    # Example: "word..word" -> "word.word"
    cleaned_text = re.sub(r'([.,;!?:])\1+', r'\1', cleaned_text)
    
    cleaned_text = cleaned_text.strip()

    cleaned_text = re.sub(r' +', ' ', cleaned_text)

    # Step 6: Unicode Normalization (Optional but good practice)
    # import unicodedata
    # cleaned_text = unicodedata.normalize('NFKC', cleaned_text)

    return cleaned_text 

def split_text_into_chunks(text: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> List[str]:
    """
    Splits the cleaned text into smaller, overlapping chunks suitable for embedding.
    """
    if not isinstance(text, str) or not text.strip():
        return []

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
    )
    chunks = text_splitter.split_text(text)
    return chunks

if __name__ == '__main__':
    print("--- Testing text_splitter functions ---")

    sample_raw_text = """
    John Doe
    Software Engineer

    Experience:
    Senior Developer at Tech Solutions Inc. (2020-Present)
    - Led development of new features.

    Junior Dev at XYZ Corp (2018-2020)
    - Assisted in various projects.

    Education:
    B.S. Computer Science - University of ABC (2014-2018)

    Skills:
    Python, Java, AWS, Docker, Kubernetes

    Page 1 of 2
    This is some additional text on page 1.


    More info on page 2.
    Certifications: AWS Certified Developer.
    Projects: Developed an e-commerce platform.
    1 | 2
    Final notes.
    """

    print("\n--- Original Raw Text ---")
    print(sample_raw_text)
    print(f"Original length: {len(sample_raw_text)}")

    cleaned = clean_text(sample_raw_text)
    print("\n--- Cleaned Text ---")
    print(cleaned)
    print(f"Cleaned length: {len(cleaned)}")

    # Test with custom chunk sizes
    chunks_default = split_text_into_chunks(cleaned)
    print(f"\n--- Chunks (Default: size={1000}, overlap={200}) ---")
    for i, chunk in enumerate(chunks_default):
        print(f"Chunk {i+1} (len: {len(chunk)}):\n'{chunk[:150]}...'")
    print(f"Total chunks: {len(chunks_default)}")

    chunks_small = split_text_into_chunks(cleaned, chunk_size=200, chunk_overlap=50)
    print(f"\n--- Chunks (Small: size={200}, overlap={50}) ---")
    for i, chunk in enumerate(chunks_small):
        print(f"Chunk {i+1} (len: {len(chunk)}):\n'{chunk[:100]}...'")
    print(f"Total chunks: {len(chunks_small)}")

    # Test edge cases
    print("\n--- Testing Edge Cases ---")
    print("Empty text cleanup:", clean_text(""))
    print("Whitespace text cleanup:", clean_text("   \n\t  "))
    print("Empty text chunking:", split_text_into_chunks(""))
    print("Whitespace text chunking:", split_text_into_chunks("   \n\t  "))