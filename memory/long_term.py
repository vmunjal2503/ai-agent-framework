"""
Long-term memory — persistent knowledge storage using ChromaDB.
"""

import os
from typing import Optional

try:
    import chromadb
    from openai import OpenAI
    HAS_DEPS = True
except ImportError:
    HAS_DEPS = False


class LongTermMemory:
    """
    Persistent vector memory for storing and retrieving knowledge.
    Uses ChromaDB for vector storage and OpenAI for embeddings.
    """

    def __init__(self, collection_name: str = "agent_memory"):
        if not HAS_DEPS:
            raise ImportError("Install chromadb and openai: pip install chromadb openai")

        self.client = chromadb.PersistentClient(path="./chromadb_data")
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},
        )
        self.openai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = "text-embedding-3-small"

    def store(self, content: str, metadata: dict = None, doc_id: str = None):
        """Store a piece of knowledge in long-term memory."""
        import uuid
        doc_id = doc_id or str(uuid.uuid4())

        embedding = self._embed(content)
        self.collection.add(
            ids=[doc_id],
            embeddings=[embedding],
            documents=[content],
            metadatas=[metadata or {}],
        )

    def recall(self, query: str, top_k: int = 3) -> list[dict]:
        """Retrieve relevant memories for a query."""
        embedding = self._embed(query)
        results = self.collection.query(
            query_embeddings=[embedding],
            n_results=top_k,
            include=["documents", "metadatas", "distances"],
        )

        memories = []
        for i in range(len(results["ids"][0])):
            memories.append({
                "content": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
                "relevance": 1 - results["distances"][0][i],
            })
        return memories

    def _embed(self, text: str) -> list[float]:
        """Generate embedding for text."""
        response = self.openai.embeddings.create(model=self.model, input=text)
        return response.data[0].embedding
