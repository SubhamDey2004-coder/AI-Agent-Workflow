def build_context(results):
    """
    Convert retrieved document chunks into a clean context
    that can be given to the language model.
    """
    
    if not results:
        return "No relevant information was found."
    
    context_parts = []
    
    for i, result in enumerate(results, start=1):
        filename = result["filename"]
        content = result["content"]
        similarity = result["similarity"]
        
        context_parts.append(
            f"[Source {i}: {filename} | similarity: {similarity} {similarity:.3f}]\n"
            f"{content}"
        )
        
    return "\n\n".join(context_parts)

def build_rag_prompt(question, context):
    return f"""
You are an AI assistant answering questions using the user's stored documents.

Use the provided context as your primary source of truth.

Rules:
1. Answer the user's question using the provided context.
2. Do not invent facts that are not supported by the context.
3. If the context does not contain enough information, say that you do not have enough information.
4. Mention the source filename when useful.
5. Keep the answer concise and clear.

USER QUESTION:
{question}

RELEVANT CONTEXT:
{context}
"""
