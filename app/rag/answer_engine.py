from groq import Groq

from app.config import GROQ_API_KEY
from app.rag.query_engine import retrieve_context


# -----------------------------
# INIT GROQ
# -----------------------------
client = Groq(api_key=GROQ_API_KEY)


# -----------------------------
# GENERATE ANSWER
# -----------------------------
def generate_answer(prompt):

    try:

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a helpful teaching assistant. "
                        "Answer ONLY using the provided context."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        return response.choices[0].message.content

    except Exception as e:

       print("LLM ERROR:", e)

       return "An internal AI error occurred."


# -----------------------------
# MAIN RAG FUNCTION
# -----------------------------
def answer_question(question):

    # retrieve context
    context, citations = retrieve_context(question)

    # fallback
    if not context.strip():

        return {
            "answer": "I don't know based on the documents.",
            "citations": []
        }

    # prompt
    prompt = f"""
Use ONLY the context below to answer the question.

If the answer is not in the context, say:
"I don't know based on the documents."

Context:
{context}

Question:
{question}

Answer clearly and concisely.
"""

    # generate
    answer = generate_answer(prompt)

    return {
        "answer": answer,
        "citations": citations
    }