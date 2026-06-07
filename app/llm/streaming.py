from groq import Groq
from app.config import GROQ_API_KEY, GROQ_ENABLED

client = Groq(api_key=GROQ_API_KEY) if GROQ_ENABLED else None


def stream_answer(prompt: str):

    if not GROQ_ENABLED:
        yield "⚠️ Groq API not configured. Please set GROQ_API_KEY."
        return

    try:
        stream = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a precise teaching assistant."},
                {"role": "user", "content": prompt}
            ],
            stream=True,
        )

        for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                yield delta

    except Exception as e:
        yield f"❌ Streaming error: {str(e)}"