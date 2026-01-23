import chromadb
from pathlib import Path

# Get the project root directory (backend's parent)
PROJECT_ROOT = Path(__file__).parent.parent.parent
CHROMA_DIR = PROJECT_ROOT / "chroma_data"

# Create PersistentClient for persistent storage
client = chromadb.PersistentClient(
    path=str(CHROMA_DIR),
    settings=chromadb.Settings(anonymized_telemetry=False)
)

collection = client.get_or_create_collection(
    name="journal_memories"
)
