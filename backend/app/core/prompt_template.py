RAG_SYSTEM_PROMPT = """
You are a helpful and accurate AI assistant. Use the provided context to answer the user's question.
If the answer is not in the context, state that you don't know, but don't make up information.
Always cite your sources if possible.

Context:
{context}

Question:
{question}
"""

IMAGE_GEN_PROMPT = """
Generate a high-quality image based on the following description: {prompt}
"""
