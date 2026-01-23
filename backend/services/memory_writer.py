from .embeddings import embed_text
from ..db.chroma import collection

def write_memory(
    *,
    message_id: int,
    session_id: str,
    role: str,
    content: str,
):
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
