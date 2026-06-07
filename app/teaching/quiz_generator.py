from openai import OpenAI
from app.config import *

client = OpenAI(api_key=OPENAI_API_KEY)


def generate_quiz(contexts, num_questions=5, difficulty="medium"):
    context_block = "\n\n".join(contexts)

    prompt = f"""
Generate {num_questions} {difficulty}-level questions based ONLY on this content.

Include:
- conceptual
- technical/code
- tricky edge-case

Content:
{context_block}
"""

    res = client.chat.completions.create(
        model=LLM_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
    )

    return res.choices[0].message.content