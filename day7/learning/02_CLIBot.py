import sys
sys.stdout.reconfigure(encoding="utf-8")  # Windows console defaults to cp1252, which can't print emoji

import os
from pathlib import Path

from dotenv import load_dotenv
from litellm import completion

# Configuration
load_dotenv(Path(__file__).resolve().parents[1] / ".env")
MODEL = os.getenv("TARGET_MODEL", "").strip()
if not MODEL:
    raise RuntimeError("TARGET_MODEL is missing or empty in the project .env file")
OLLAMA = "http://localhost:11434"

def main():
    # Initialize session state (conversation history)
    # The system prompt sets the behavior of the AI
    messages = [
        {
            'role': 'system',
            'content': 'You are a helpful, witty, and concise AI assistant.'
        }
    ]

    print("Local Ollama Chatbot Initialized")
    print("Type your question and press Enter. Type 'exit' or 'quit' to end.")

    while True:
        try:
            user_input = input("\nYou: ").strip()

            if user_input.lower() in ['exit', 'quit']:
                print("\nGoodbye! Thanks for chatting.")
                break
            if not user_input:
                continue

            messages.append({'role': 'user', 'content': user_input})

            response = completion(
                model=MODEL,
                messages=messages,
                api_base=OLLAMA,
                stream=True
            )

            print("AI: ", end="", flush=True)
            full_response = ""
            for chunk in response:
                content = chunk.choices[0].delta.content
                if content:
                    print(content, end="", flush=True)
                    full_response += content
            print()

            messages.append({'role': 'assistant', 'content': full_response})

        except KeyboardInterrupt:
            print("\n\nSession interrupted. Goodbye!")
            break

if __name__ == "__main__":
    main()
