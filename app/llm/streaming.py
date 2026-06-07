from groq import Groq
from app.config import GROQ_API_KEY

# =================================
# INIT CLIENT
# =================================
client = Groq(api_key=GROQ_API_KEY)


# =================================
# STREAMING FUNCTION
# =================================
def stream_answer(prompt: str):

    try:

        stream = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a precise, structured teaching assistant. "
                        "Answer clearly and accurately."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            stream=True,
        )

        for chunk in stream:

            delta = chunk.choices[0].delta.content

            if delta:
                yield delta

    except Exception as e:
        yield f"\n❌ Streaming error: {str(e)}"

