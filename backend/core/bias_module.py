import spacy
from spacy.lang.en import English
import re
from typing import Optional, List

_nlp: Optional[spacy.Language] = None

def _initialize_nlp_model():
    """Initializes the SpaCy model if it's not already loaded."""
    global _nlp
    if _nlp is None:
        try:
            print("Initializing SpaCy model 'en_core_web_sm'...")
            _nlp = spacy.load("en_core_web_sm")
            print("SpaCy model initialized successfully.")
        except OSError:
            print("SpaCy model not found. Please run 'python -m spacy download en_core_web_sm'")
            _nlp = English()
            _nlp.add_pipe("sentencizer")

def anonymize_text(text: str) -> str: 
    if _nlp is None:
        _initialize_nlp_model()
    
    doc = _nlp(text)
    
    anonymized_text = list(text)

    entities_to_anonymize = ["PERSON", "GPE", "NORP", "DATE", "ORG"]
    for ent in reversed(doc.ents):
        if ent.label_ in entities_to_anonymize:
            placeholder = f"[{ent.label_}]"
            anonymized_text[ent.start_char:ent.end_char] = list(placeholder)

    current_text = "".join(anonymized_text)
    
    email_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    current_text = re.sub(email_regex, '[EMAIL]', current_text)

    phone_regex = r'(\(?\d{3}\)?[-.\s]?){1,2}\d{3}[-.\s]?\d{4}'
    current_text = re.sub(phone_regex, '[PHONE]', current_text)
    
    return current_text

def anonymize_chunks(chunks: List[str]) -> List[str]:
    """Applies anonymization to a list of text chunks."""
    return [anonymize_text(chunk) for chunk in chunks]

_initialize_nlp_model()