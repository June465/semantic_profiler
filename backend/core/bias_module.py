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
            # Fallback to a blank model to avoid crashing, though NER will not work
            _nlp = English()
            _nlp.add_pipe("sentencizer")

def anonymize_text(text: str) -> str:
    """
    Anonymizes text by removing personally identifiable information (PII)
    using SpaCy for Named Entity Recognition (NER) and regex for patterns.
    """
    if _nlp is None:
        _initialize_nlp_model()
    
    # Process the text with SpaCy
    doc = _nlp(text)
    
    anonymized_text = list(text)

    # Replace named entities with placeholders
    # Common PII labels: PERSON (names), GPE (locations), NORP (nationalities, religious/political groups)
    entities_to_anonymize = ["PERSON", "GPE", "NORP", "DATE", "ORG"]
    for ent in reversed(doc.ents):
        if ent.label_ in entities_to_anonymize:
            # Replace entity text with a generic placeholder
            placeholder = f"[{ent.label_}]"
            anonymized_text[ent.start_char:ent.end_char] = list(placeholder)

    # Convert list back to string for regex operations
    current_text = "".join(anonymized_text)
    
    # Regex for emails
    email_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    current_text = re.sub(email_regex, '[EMAIL]', current_text)

    # Regex for phone numbers (basic patterns)
    phone_regex = r'(\(?\d{3}\)?[-.\s]?){1,2}\d{3}[-.\s]?\d{4}'
    current_text = re.sub(phone_regex, '[PHONE]', current_text)
    
    return current_text

def anonymize_chunks(chunks: List[str]) -> List[str]:
    """Applies anonymization to a list of text chunks."""
    return [anonymize_text(chunk) for chunk in chunks]

# Initialize the model on module load to have it ready
_initialize_nlp_model()