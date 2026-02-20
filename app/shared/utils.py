from datetime import datetime
from google.api_core.datetime_helpers import DatetimeWithNanoseconds
import re
import unicodedata

def serialize_firestore(value):
    if isinstance(value, DatetimeWithNanoseconds):
        return value.isoformat()

    if isinstance(value, datetime):
        return value.isoformat()

    if isinstance(value, dict):
        return {k: serialize_firestore(v) for k, v in value.items()}

    if isinstance(value, list):
        return [serialize_firestore(v) for v in value]

    return value



STOP_WORDS = {
    'de', 'la', 'las', 'el', 'los', 'del', 'y', 'en', 'a', 'e', 'o', 'u',
}

MIN_PREFIX_LEN = 3

def normalize_text(text: str) -> str:
    if not text:
        return ""
    # Convertir a minúsculas
    text = text.lower()
    # Normalizar NFD y eliminar acentos (caracteres Mn)
    text = "".join(c for c in unicodedata.normalize('NFD', text)
                  if unicodedata.category(c) != 'Mn')
    # Eliminar caracteres no alfanuméricos excepto espacios
    text = re.sub(r'[^a-z0-9\s]', '', text)
    return text.strip()

def generate_search_tokens(display_name: str) -> list[str]:
    if not display_name:
        return []
    
    tokens = set()
    normalized = normalize_text(display_name)
    words = [word for word in normalized.split() 
             if word and word not in STOP_WORDS]

    for word in words:
        if len(word) < MIN_PREFIX_LEN:
            tokens.add(word)
        else:
            for i in range(MIN_PREFIX_LEN, len(word) + 1):
                tokens.add(word[:i])
    
    return sorted(list(tokens))