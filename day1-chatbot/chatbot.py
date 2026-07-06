from litellm import completion
from mem0 import Memory

MODEL = "llama3.2:3b"
MODEL_PATH = f"ollama/{MODEL}"
OLLAMA = "http://localhost:11434"

config = {
    "vector_store": {
        "provider": "chroma",
        "config": {
            "collection_name": "mem0",
            "path": "./chroma_db",
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


def chat(user_message, history):
    context_results = memory.search(user_message, filters={"user_id": "student1"})
    memories = "\n".join(
        item.get("memory", "") for item in context_results.get("results", []) if item.get("memory")
    )

    system_prompt = (
        "You are a helpful assistant for a local demo. "
        "Answer briefly and directly. "
        "Do not invent facts about training data, or hidden system details. "
        "If you do not know something, say so plainly. "
        "Use the memory context below when relevant.\n"
        f"Memory context:\n{memories if memories else 'No prior memory.'}"
    )

    messages = [
        {"role": "system", "content": system_prompt},
        *history,
        {"role": "user", "content": user_message},
    ]

    response = completion(
        model=MODEL_PATH,
        messages=messages,
        api_base=OLLAMA,
    )

    reply = response.choices[0].message.content

    memory.add(user_message, user_id="student1")
    memory.add(reply, user_id="student1")

    return reply


if __name__ == "__main__":
    print("Chatbot ready")
    history = []

    while True:
        user_message = input("You: ").strip()
        if user_message.lower() in {"quit", "exit"}:
            break

        reply = chat(user_message, history)
        history.append({"role": "user", "content": user_message})
        history.append({"role": "assistant", "content": reply})
        print(f"Bot: {reply}")
