import re
from typing import List
from langchain.text_splitter import RecursiveCharacterTextSplitter

def clean_text(text: str) -> str:

    if not isinstance(text, str):
        return ""

    cleaned_text = str(text)

    page_number_patterns = r'\bPage\s+\d+\s+of\s+\d+\b|\b\d+\s*\|\s*\d+\b|\b\d+/\d+\b'
    cleaned_text = re.sub(page_number_patterns, '', cleaned_text, flags=re.IGNORECASE)

    cleaned_text = re.sub(r'\s+', ' ', cleaned_text)

    cleaned_text = re.sub(r'\s+([.,;!?:])', r'\1', cleaned_text)

    cleaned_text = re.sub(r'([.,;!?:])\1+', r'\1', cleaned_text)
    
    cleaned_text = cleaned_text.strip()

    cleaned_text = re.sub(r' +', ' ', cleaned_text)

    # import unicodedata
    # cleaned_text = unicodedata.normalize('NFKC', cleaned_text)

    return cleaned_text 

def split_text_into_chunks(text: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> List[str]:
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

    print("\n--- Testing Edge Cases ---")
    print("Empty text cleanup:", clean_text(""))
    print("Whitespace text cleanup:", clean_text("   \n\t  "))
    print("Empty text chunking:", split_text_into_chunks(""))
    print("Whitespace text chunking:", split_text_into_chunks("   \n\t  "))