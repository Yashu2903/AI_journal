"""AI-related operations: embeddings, LLM, and prompt building."""
from sentence_transformers import SentenceTransformer
import ollama

# Initialize embedding model
_embedding_model = SentenceTransformer("all-MiniLM-L6-v2")


def embed_text(text: str) -> list[float]:
    """Generate embeddings for text using sentence transformers."""
    return _embedding_model.encode(text).tolist()


def generate_reply(messages: list[dict]) -> str:
    """Generate a reply using Ollama LLM."""
    response = ollama.chat(
        model="llama3.1",
        messages=messages
    )
    return response["message"]["content"]


def build_prompt(
    *,
    history: list[dict],
    memories: list[str]
) -> list[dict]:
    """Build a prompt with system message, memories, and conversation history."""
    system_message = {
        "role": "system",
        "content": (
            "You are an AI assistant with access to past memories.\n"
            "When memories are provided, you MUST use them to answer.\n"
            "If memories are relevant, refer to them naturally.\n"
            "If not, answer normally.\n"
        )
    }

    memory_block = {
        "role": "system",
        "content": "PAST MEMORIES:\n" + "\n".join(f"- {m}" for m in memories)
    } if memories else None

    messages = [system_message]

    if memory_block:
        messages.append(memory_block)

    messages.extend(history)

    return messages
