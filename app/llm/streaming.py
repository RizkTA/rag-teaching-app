from groq import Groq
from app.config import GROQ_API_KEY

client = Groq(api_key=GROQ_API_KEY)


def stream_answer(prompt: str):

    if not GROQ_API_KEY:
        yield "⚠️ GROQ_API_KEY missing"
        return

    try:
        stream = client.chat.completions.create(
            model="llama-3.3-70b-versatile",  # or llama-3.3-70b-versatile
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