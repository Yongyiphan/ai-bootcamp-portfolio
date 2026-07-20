from litellm import completion
import day7.lecture.config as config

def get_ollama_stream(model_name, conversation_history, fresh_prompt):
    payload = conversation_history + [{"role": "user", "content": fresh_prompt}]
    ollama_model = model_name.removeprefix("ollama/")
    return completion(
        model=f"ollama/{ollama_model}",
        messages=payload,
        api_base=config.OLLAMA_API_BASE,
        stream=True
    )

def parse_stream_chunks(raw_stream):
    for chunk in raw_stream:
        content = chunk.choices[0].delta.content
        if content:
            yield content
