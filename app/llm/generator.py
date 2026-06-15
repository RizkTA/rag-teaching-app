import os
from groq import Groq

# =============================
# INIT GROQ
# =============================
client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

# =============================
# CONFIG
# =============================
MAX_CONTEXT_CHARS = 5000

SYSTEM_PROMPT = """
You are RIZK AI Assistant,
a strict university teaching assistant.

RULES:
- Answer ONLY from the provided context.
- If the answer is not found, say:
  "I don't know based on the documents."
- Be concise.
- Prefer code examples when available.
- Do NOT invent information.
- If context contains code:
  return formatted code blocks.
- Avoid repeating the question.
"""

# =============================
# GENERATE ANSWER
# =============================
def generate_answer(query, contexts):

    try:

        # =============================
        # NO CONTEXT
        # =============================
        if not contexts:
            return "⚠️ No relevant content found in your documents."

        # =============================
        # CLEAN CONTEXTS
        # =============================
        cleaned_contexts = []

        for c in contexts[:5]:

            if isinstance(c, dict):
                text = c.get("text", "")
            else:
                text = str(c)

            if text.strip():
                cleaned_contexts.append(text.strip())

        # =============================
        # BUILD CONTEXT
        # =============================
        context_text = "\n\n".join(cleaned_contexts)

        # prevent huge prompts
        context_text = context_text[:MAX_CONTEXT_CHARS]

        # =============================
        # PROMPT
        # =============================
        prompt = f"""
CONTEXT:
{context_text}

QUESTION:
{query}

ANSWER:
"""

        # =============================
        # LLM CALL
        # =============================
        response = client.chat.completions.create(

            model="llama-3.3-70b-versatile",

            temperature=0.1,

            max_tokens=700,

            messages=[

                {
                    "role": "system",
                    "content": SYSTEM_PROMPT
                },

                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        answer = response.choices[0].message.content.strip()

        # =============================
        # EMPTY SAFETY
        # =============================
        if not answer:
            return "I don't know based on the documents."

        return answer

    except Exception as e:

        print("GENERATOR ERROR:", e)

        return "⚠️ AI generation failed."
