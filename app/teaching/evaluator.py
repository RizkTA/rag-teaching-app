from openai import OpenAI
from app.config import *

client = OpenAI(api_key=OPENAI_API_KEY)


def evaluate_answer(question, student_answer, contexts):
    context_block = "\n\n".join(contexts)

    prompt = f"""
Grade the student's answer based ONLY on the context.

Question: {question}
Student Answer: {student_answer}

Context:
{context_block}

Return:
- score (0-10)
- feedback
- correct answer
"""

    res = client.chat.completions.create(
        model=LLM_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )

    return res.choices[0].message.content