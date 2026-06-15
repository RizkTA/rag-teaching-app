import ollama

def stream_answer(prompt: str):
    response = ollama.generate(
        model="llama3",
        prompt=prompt,
        stream=False
    )

    return response["response"]