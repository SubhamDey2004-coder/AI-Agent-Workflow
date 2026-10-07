from persistent_search import search_index

def search_knowledge(query):

    results = search_index(query, top_k=3)

    if not results:
        return {
            "found": False,
            "message": "No sufficiently relevant information was found in the user's indexed documents."
        }

    return {
        "found": True,
        "results": [
            {
                "filename": result["filename"],
                "chunk_index": result["chunk_index"],
                "content": result["content"],
                "similarity": result["similarity"]
            }
            for result in results
        ]
    }