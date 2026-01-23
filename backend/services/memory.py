"""Memory operations for reading and writing to ChromaDB."""
from ..db.chroma import collection
from .ai import embed_text


def recall_memories(
    query: str,
    session_id: str,
    k: int = 5
) -> list[str]:
    """Recall relevant memories from ChromaDB based on query."""
    results = collection.query(
        query_texts=[query],
        n_results=k,
        where={"session_id": session_id}
    )

    if not results["documents"]:
        return []

    docs = results["documents"][0]
    return [d for d in docs if len(d) > 20]


def write_memory(
    *,
    message_id: int,
    session_id: str,
    role: str,
    content: str,
) -> None:
    """Write a memory to ChromaDB with embeddings."""
    vector = embed_text(content)

    collection.upsert(
        ids=[f"msg_{message_id}"],
        documents=[content],
        embeddings=[vector],
        metadatas=[{
            "session_id": session_id,
            "role": role
        }]
    )
