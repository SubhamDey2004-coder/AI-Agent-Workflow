import os
import math

from memory import get_embedding
from file_tools import list_files, read_file


def cosine_similarity(a, b):

    dot_product = sum(x * y for x, y in zip(a, b))

    magnitude_a = math.sqrt(sum(x * x for x in a))
    magnitude_b = math.sqrt(sum(x * x for x in b))

    if magnitude_a == 0 or magnitude_b == 0:
        return 0.0

    return dot_product / (magnitude_a * magnitude_b)


def semantic_search(query, top_k=3):

    query_embedding = get_embedding(query)

    results = []

    for filename in list_files():

        content = read_file(filename)

        if content.startswith("Error:") or content.startswith("File not found"):
            continue

        file_embedding = get_embedding(content)

        similarity = cosine_similarity(
            query_embedding,
            file_embedding
        )

        results.append({
            "filename": filename,
            "similarity": similarity
        })

    results.sort(
        key=lambda x: x["similarity"],
        reverse=True
    )

    return results[:top_k]