"""
PROJECT 1 — Context-Aware Chatbot with Memory

Your task is to build a chatbot that can remember useful information from
previous messages and use that memory to answer later questions.

This chatbot should be able to:

1. Build a working chatbot interface
   - You may use Gradio or a simple CLI.
   - The chatbot should accept user input and return an AI response.

2. Maintain conversation history
   - Store both user messages and assistant replies.
   - Use recent conversation history so the chatbot can understand context.

3. Store memory
   - Use JSON, SQLite, or ChromaDB.
   - For the basic version, SQLite or JSON is enough.
   - Each message should be saved with at least:
       role      -> "user" or "assistant"
       content   -> the message text
       timestamp -> when the message was saved

4. Retrieve relevant memory
   - Do not send the entire history to the model every time.
   - Retrieve only useful memory.
   - Basic version: keyword search.
   - Advanced version: semantic search using embeddings / ChromaDB.

5. Use provided files from Moodle
   - Load skills.md as learner profile or background knowledge.
   - Load memory_seed.json as structured starting memory.
   - Add both into the system prompt when helpful.

6. Apply prompt engineering
   - Write a clear system prompt.
   - Tell the model how to use memory.
   - Tell the model not to invent personal facts.
   - Tell the model to say “I don’t know” if memory does not contain the answer.

7. Bonus features
   - Add summarization when the conversation becomes long.
   - Support multiple users with separate memory.
   - Improve latency by limiting how much memory is sent to the model.

Suggested structure:

- setup database / memory file
- load skills.md
- load memory_seed.json
- save_memory()
- search_memory()
- get_recent_history()
- build_messages()
- chat_bot()
- Gradio or CLI interface

Important idea:
main chatbot function should not do everything by itself.
It should coordinate smaller helper functions, similar to the AI pipeline idea:
input -> retrieve memory -> build prompt -> call model -> save response -> return output.
"""