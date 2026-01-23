from ..db.chroma import collection

def recall_memories(
    query: str,
    session_id: str,
    k: int = 5
) -> list[str]:
    results = collection.query(
        query_texts=[query],
        n_results=k,
        where={"session_id": session_id}
    )

    if not results["documents"]:
        return []

    docs = results["documents"][0]
    return [d for d in docs if len(d) > 20]
