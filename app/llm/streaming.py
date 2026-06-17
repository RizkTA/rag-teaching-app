# streaming.py
from groq import Groq
import os

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

def stream_answer(prompt: str):

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        temperature=0.1,
        max_tokens=700,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.choices[0].message.content