import math

from memory import get_embedding
from vector_store import load_index


def cosine_similarity(a, b):

    dot_product = sum(x * y for x, y in zip(a, b))

    magnitude_a = math.sqrt(sum(x * x for x in a))
    magnitude_b = math.sqrt(sum(x * x for x in b))

    if magnitude_a == 0 or magnitude_b == 0:
        return 0.0

    return dot_product / (magnitude_a * magnitude_b)


def search_index(query, top_k=3, min_similarity=0.60):

    query_embedding = get_embedding(query)

    index = load_index()

    results = []

    for record in index:

        similarity = cosine_similarity(
            query_embedding,
            record["embedding"]
        )

        results.append({
            "filename": record["filename"],
            "chunk_index": record["chunk_index"],
            "content": record["content"],
            "similarity": similarity
        })

    results.sort(
        key=lambda x: x["similarity"],
        reverse=True
    )
    
    results = [
        result
        for result in results
        if result["similarity"] >= min_similarity
    ]

    return results[:top_k]