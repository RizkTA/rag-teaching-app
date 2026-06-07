import os
from groq import Groq

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def generate_answer(query, contexts):

    if not contexts:
        return "⚠️ No relevant content found in your documents."

    context_text = "\n\n".join(contexts[:4])

    prompt = f"""
You are a strict teaching assistant.

Use ONLY this context:

{context_text}

Question: {query}
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You are a strict teaching assistant."},
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content
