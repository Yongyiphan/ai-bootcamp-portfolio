# Memory Chatbot with Mem0 and Streamlit

A stateful conversational AI that remembers user interactions using vector-based semantic memory storage.

## Features

- **Long-term Memory**: Uses Mem0 to store and retrieve facts from conversations
- **Semantic Search**: Searches memory by meaning (not just keywords) using ChromaDB + nomic-embed-text
- **Local LLM**: Runs on Ollama with llama3.2:3b (fast, lightweight)
- **Web UI**: Streamlit-powered chat interface with conversation history
- **Terminal CLI**: Simple Python script for command-line chatting

## Architecture

```
chatbot.py          → Core chat logic with Mem0 integration
app.py              → Streamlit web UI wrapper
memory_setup.py     → Standalone memory demo/test
test_model.py       → LiteLLM + Ollama test
```

## Quick Start

### Prerequisites

- Python 3.13+
- Ollama running locally (port 11434)
- Models installed: `llama3.2:3b` and `nomic-embed-text`

### Installation

```bash
cd day1-chatbot
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt  # if available, or install manually
```

### Run Streamlit Web UI (Recommended)

```bash
.\venv\Scripts\streamlit.exe run app.py
```

Then open **http://localhost:8501** in your browser.

### Run Terminal Chatbot

```bash
.\venv\Scripts\python.exe chatbot.py
```

Type messages and press Enter. Exit with `quit` or `exit`.

### Test Memory Setup

```bash
.\venv\Scripts\python.exe memory_setup.py
```

## Configuration

### LLM Model
Edit the `MODEL` variable in `chatbot.py`:
```python
MODEL = "llama3.2:3b"  # Change to another Ollama model
```

### Ollama Base URL
Change `OLLAMA` in `chatbot.py` if running on a different host/port:
```python
OLLAMA = "http://localhost:11434"
```

### Memory Storage
ChromaDB stores memories in `./chroma_db/` (created automatically).

## Dependencies

- **litellm**: LLM API abstraction
- **mem0**: Memory management framework
- **chromadb**: Vector database for memory storage
- **ollama**: Local LLM inference
- **streamlit**: Web UI framework
- **spacy**: NLP text processing (optional, for lemmatization)

## How It Works

1. **User Input** → Search memory for context using semantic similarity
2. **Build Prompt** → Combine system instructions + memory results + user message
3. **Generate Response** → Call LLM (llama3.2:3b via Ollama)
4. **Store Memory** → Save both user message and assistant response to ChromaDB
5. **Display** → Show response in UI or terminal

## Example Conversation

```
You: My name is Alex
Bot: Nice to meet you, Alex!

You: What's my name?
Bot: Your name is Alex.
```

The chatbot retrieves the stored fact from memory and uses it in context.

## Performance Notes

- **Response Time**: 2-5 seconds per message (depends on Ollama hardware)
- **Memory Size**: Grows with every message (currently stored forever)
- **Database**: `./chroma_db/` persists between sessions

## Troubleshooting

### Model Not Found
Ensure the model is pulled in Ollama:
```bash
ollama pull llama3.2:3b
ollama pull nomic-embed-text
```

### Memory Warnings
Ignore warnings about ChromaDB not supporting hybrid search or PostHog clients—they don't affect functionality.

### Slow Responses
Try a smaller model:
```bash
ollama pull phi3:mini
```

Then update `MODEL` in `chatbot.py`.

## Files

- `chatbot.py` - Main chat function and terminal interface
- `app.py` - Streamlit web UI
- `memory_setup.py` - Standalone memory demo
- `test_model.py` - LiteLLM/Ollama test script
- `.chroma_db/` - Vector database (auto-created)

## License

This is a demo project for learning AI, LLMs, and memory systems.
