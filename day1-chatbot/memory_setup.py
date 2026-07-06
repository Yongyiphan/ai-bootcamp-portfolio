import shutil
from pathlib import Path

from mem0 import Memory

MODEL = "gemma4:e2b"
OLLAMA = "http://localhost:11434"
DB_PATH = Path("./chroma_db")

if DB_PATH.exists():
    shutil.rmtree(DB_PATH)

config = {
    "vector_store": {
        "provider": "chroma",
        "config": {
            "collection_name": "mem0",
            "path": str(DB_PATH),
        },
    },
    "embedder": {
        "provider": "ollama",
        "config": {
            "model": "nomic-embed-text",
            "ollama_base_url": OLLAMA,
        },
    },
    "llm": {
        "provider": "ollama",
        "config": {
            "model": MODEL,
            "ollama_base_url": OLLAMA,
        },
    },
}

memory = Memory.from_config(config)

memory.add("My name is Alex and I study at DigiPen", user_id="student1")
results = memory.search("What is my name?", filters={"user_id": "student1"})
print(results)
