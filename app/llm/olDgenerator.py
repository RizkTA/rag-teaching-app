from openai import OpenAI
from app.config import *

client = OpenAI(api_key=OPENAI_API_KEY)


def generate_answer(query, contexts):
    context_block = "\n\n".join(contexts)

    prompt = f"""
Use the context below to answer the question.

Context:
{context_block}

Question: {query}
Answer concisely:
"""

    res = client.chat.completions.create(
        model=LLM_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )

    return res.choices[0].message.content