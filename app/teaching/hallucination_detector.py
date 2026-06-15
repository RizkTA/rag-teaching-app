import json
from openai import OpenAI
from app.config import *

client = OpenAI(api_key=OPENAI_API_KEY)

def detect_hallucination_structured(question, answer, contexts):
    context_block = "\n\n".join(contexts)

    prompt = f"""
You are a strict evaluator.

Given:
- Question
- Answer
- Context

Return ONLY valid JSON with:
- hallucination_score (0..1)
- grounded (true/false)
- explanation (short string)
- unsupported_spans (list of exact substrings from the answer that are NOT supported by the context)

Rules:
- Spans must be exact substrings from the answer
- If everything is supported, return an empty list for unsupported_spans

Question:
{question}

Answer:
{answer}

Context:
{context_block}
"""

    res = client.chat.completions.create(
        model=LLM_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )

    raw = res.choices[0].message.content.strip()

    # Be defensive: ensure valid JSON
    try:
        return json.loads(raw)
    except Exception:
        return {
            "hallucination_score": 0.5,
            "grounded": False,
            "explanation": "Parser fallback. Model did not return strict JSON.",
            "unsupported_spans": []
        }