"""
Matcher de carreras usando similaridad semántica.
Recibe un string de carrera y retorna el objeto degree más cercano del catálogo.
"""

import re
import math
import unicodedata
from typing import Optional
import google.generativeai as genai


DEGREE_EMBEDDING_DIM = 512


def sanitize_degree_display(raw: str) -> str:
    """Normaliza el displayName de una carrera."""
    text = str(raw).strip()
    # NFC normalization
    text = unicodedata.normalize('NFC', text)
    # Remove special characters, keep only letters, numbers, spaces
    text = re.sub(r'[^\p{L}\p{N}\s]', '', text, flags=re.UNICODE)
    # Single spaces
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def is_valid_embedding(arr) -> bool:
    """Valida que sea un array de números válidos."""
    if not isinstance(arr, list):
        return False
    if len(arr) == 0:
        return False
    return all(isinstance(x, (int, float)) and math.isfinite(float(x)) for x in arr)


def cosine_similarity(a: list[float], b: list[float]) -> float:
    """Calcula similaridad coseno entre dos vectores."""
    if not a or len(a) != len(b):
        return -1.0

    dot_product = sum(va * vb for va, vb in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))

    if norm_a == 0 or norm_b == 0:
        return -1.0

    return dot_product / (norm_a * norm_b)


async def generate_degree_embedding(display_name: str, api_key: str) -> Optional[list[float]]:
    """Genera embedding usando Google Gemini."""
    text = sanitize_degree_display(display_name)
    if not text:
        raise ValueError("El displayName no puede estar vacío para generar embedding")

    genai.configure(api_key=api_key)
    model = "embedding-001"

    result = genai.embed_content(
        model=model,
        content=text,
        task_type="SEMANTIC_SIMILARITY",
        output_dimensionality=DEGREE_EMBEDDING_DIM
    )

    embedding = result.get('embedding')
    if not embedding or not is_valid_embedding(embedding):
        raise ValueError("Gemini no devolvió un embedding válido")

    return embedding


def find_best_career_match(
    user_embedding: list[float],
    catalog_careers: list[dict]
) -> Optional[dict]:
    """
    Encuentra la carrera más similar en el catálogo usando cosine similarity.

    catalog_careers format:
    [
        {
            "id": "ingenieria_en_sistemas",
            "display": "Ingeniería en Sistemas",
            "embedding": [0.1, 0.2, ...]
        },
        ...
    ]
    """
    best_career = None
    best_score = -1.0

    for career in catalog_careers:
        if not is_valid_embedding(career.get('embedding')):
            continue

        score = cosine_similarity(user_embedding, career['embedding'])
        if score > best_score:
            best_score = score
            best_career = career

    return best_career


def match_degree(
    career_input: str,
    catalog_careers: list[dict],
    embedding: Optional[list[float]] = None,
    api_key: Optional[str] = None
) -> dict:
    """
    Recibe un career string y retorna el objeto degree normalizado.

    Args:
        career_input: El string de carrera ingresado por el usuario
        catalog_careers: Lista de carreras del catálogo con embeddings
        embedding: (Opcional) Embedding pre-calculado para el career_input
        api_key: API key de Gemini (requerida si embedding es None)

    Returns:
        {
            "displayName": str,
            "embedding": list[float],
            "id": str
        }

    Raises:
        ValueError: Si hay error en la normalización o generación de embedding
    """
    import asyncio

    # Normalizar displayName
    display_name = sanitize_degree_display(career_input)
    if not display_name:
        raise ValueError("Career input no válido después de normalización")

    # Generar embedding si no lo tenemos
    if embedding is None:
        if not api_key:
            raise ValueError("Se requiere api_key si no se proporciona embedding")
        embedding = asyncio.run(generate_degree_embedding(display_name, api_key))

    # Validar embedding
    if not is_valid_embedding(embedding):
        raise ValueError("Embedding no válido")

    # Encontrar carrera más similar en el catálogo
    best_match = find_best_career_match(embedding, catalog_careers)
    if not best_match:
        raise ValueError("No se encontró coincidencia en el catálogo")

    # Retornar objeto degree
    return {
        "displayName": best_match['display'],
        "embedding": embedding,
        "id": best_match['id']
    }


# Ejemplo de uso:
if __name__ == "__main__":
    import os
    import asyncio

    # Simular catálogo (normalmente viendría de Firebase)
    MOCK_CATALOG = [
        {
            "id": "ingenieria_en_sistemas",
            "display": "Ingeniería en Sistemas",
            "embedding": [0.1] * DEGREE_EMBEDDING_DIM
        },
        {
            "id": "ingenieria_en_software",
            "display": "Ingeniería en Software",
            "embedding": [0.11] * DEGREE_EMBEDDING_DIM
        },
        {
            "id": "administracion_empresas",
            "display": "Administración de Empresas",
            "embedding": [0.5] * DEGREE_EMBEDDING_DIM
        }
    ]

    # Usar así en tu API:
    # result = match_degree(
    #     career_input="Ingeniera en Sistemas",
    #     catalog_careers=MOCK_CATALOG,
    #     api_key=os.getenv("GEMINI_API_KEY")
    # )
    # print(result)
