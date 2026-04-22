import math
import google.generativeai as genai
from app.domain.model.student import Degree


DEGREE_EMBEDDING_DIM = 512


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


def generate_degree_embedding(display_name: str, api_key: str) -> list[float]:
    """Genera embedding usando Google Gemini."""
    if not display_name or not display_name.strip():
        raise ValueError("El displayName no puede estar vacío para generar embedding")

    genai.configure(api_key=api_key)
    model = "models/gemini-embedding-001"

    result = genai.embed_content(
        model=model,
        content=display_name.strip(),
        task_type="SEMANTIC_SIMILARITY",
        output_dimensionality=DEGREE_EMBEDDING_DIM
    )

    embedding = result.get('embedding')
    if not embedding or not is_valid_embedding(embedding):
        raise ValueError("Gemini no devolvió un embedding válido")

    return embedding


def generate_degree(
    career_input: str,
    catalog_careers: list[dict],
    api_key: str
) -> Degree:
    """
    Genera un objeto Degree para un career del estudiante.

    Args:
        career_input: El string de carrera ingresado por el usuario
        catalog_careers: Lista de carreras del catálogo con embeddings
        api_key: API key de Gemini

    Returns:
        Degree object con {displayName, embedding, id}

    Raises:
        ValueError: Si hay error en la generación de embedding o búsqueda
    """
    if not career_input or not career_input.strip():
        raise ValueError("Career input no válido")

    # Generar embedding para el career del estudiante
    embedding = generate_degree_embedding(career_input, api_key)

    # Encontrar la carrera más similar en el catálogo
    best_career = None
    best_score = -1.0

    for career in catalog_careers:
        if not is_valid_embedding(career.get('embedding')):
            continue

        score = cosine_similarity(embedding, career['embedding'])
        if score > best_score:
            best_score = score
            best_career = career

    if not best_career:
        raise ValueError("No se encontró coincidencia en el catálogo de carreras")

    # Retornar objeto Degree
    return Degree(
        displayName=best_career.get('display') or best_career.get('displayName'),
        embedding=embedding,
        id=best_career['id']
    )
