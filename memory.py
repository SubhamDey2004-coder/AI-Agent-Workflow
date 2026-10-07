import json
import os
import math
import ollama

MEMORY_FILE = "memory.json"

EMBEDDING_MODEL = "nomic-embed-text"

SIMILARITY_THRESHOLD = 0.50


def get_embedding(text):

    response = ollama.embed(
        model=EMBEDDING_MODEL,
        input=text
    )

    return response["embeddings"][0]

def cosine_similarity(vector_a, vector_b):

    dot_product = sum(
        a * b
        for a, b in zip(vector_a, vector_b)
    )

    magnitude_a = math.sqrt(
        sum(a * a for a in vector_a)
    )

    magnitude_b = math.sqrt(
        sum(b * b for b in vector_b)
    )

    if magnitude_a == 0 or magnitude_b == 0:
        return 0.0

    return dot_product / (magnitude_a * magnitude_b)

def load_memory():
    
    if not os.path.exists(MEMORY_FILE):
        return []
    with open(MEMORY_FILE, "r", encoding="utf-8") as file:
        return json.load(file)
    
def save_memory(memory):
    with open(MEMORY_FILE, "w", encoding="utf-8") as file:
        json.dump(memory, file, indent=4)
        
def remember(content):

    memory = load_memory()

    embedding = get_embedding(content)

    memory.append(
        {
            "content": content,
            "embedding": embedding
        }
    )

    save_memory(memory)

    return "Memory saved successfully."

def recall(query):

    memory = load_memory()

    query_embedding = get_embedding(query)

    results = []

    for item in memory:

        if "embedding" not in item:
            continue

        similarity = cosine_similarity(
            query_embedding,
            item["embedding"]
        )

        results.append(
            {
                "content": item["content"],
                "similarity": similarity
            }
        )


    results.sort(
    key=lambda item: item["similarity"],
    reverse=True
    )

    if not results:
        return []

    if results[0]["similarity"] < SIMILARITY_THRESHOLD:
        return []

    return [
        item["content"]
        for item in results[:3]
    ]

def migrate_memory():
    memory = load_memory()
    changed = False
    
    for item in memory:
        if "embedding" not in item:
            item["embedding"] = get_embedding(
                item["content"]
            )
            
            changed = True
            
    if changed:
        save_memory(memory)
    return "Memory migration completed."