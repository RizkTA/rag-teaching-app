from app.config import (
    QDRANT_URL,
    QDRANT_COLLECTION,
    EMBED_DIM,
    GROQ_API_KEY
)

from app.vectorstores.qdrant_store import QdrantStore
from app.rag.fusion_rag import fusion_search

from groq import Groq

from app.rag.mmr import  apply_mmr

# =================================
# GROQ CLIENT
# =================================
client = Groq(
    api_key=GROQ_API_KEY
)


# =================================
# CONFIG
# =================================
MAX_CONTEXT_CHARS = 6000
TOP_K = 5


# =================================
# INIT VECTOR DB
# =================================
try:

    store = QdrantStore(
        QDRANT_URL,
        QDRANT_COLLECTION,
        EMBED_DIM
    )

    print("✅ Qdrant connected")

except Exception as e:

    print("⚠️ Qdrant disabled:", e)

    store = None


# =================================
# LLM GENERATION
# =================================
def generate(prompt: str) -> str:

    try:

        response = client.chat.completions.create(

            model="llama-3.3-70b-versatile",

            messages=[

                {
                    "role": "system",

                    "content":
                        (
                            "You are a helpful teaching assistant. "
                            "Answer ONLY using the provided context. "
                            "If code exists in context, include the code."
                        )
                },

                {
                    "role": "user",
                    "content": prompt
                }
            ],

            temperature=0.2,

            max_tokens=1024
        )

        return response.choices[0].message.content

    except Exception as e:

        print("LLM ERROR:", e)

        return "An internal AI error occurred."


# =================================
# RETRIEVAL
# =================================
def retrieve(question, top_k=TOP_K):

    try:

        results = fusion_search(question)
        results = apply_mmr(
            question,
            results,
            top_k=5,
            lambda_param=0.7
        )
        results = results[:4]
        contexts = []

        citations = []

        best_chunk = None

        best_score = -999

        for r in results:

            text = r.get("text", "")

            if not text:
                continue

            score = float(
                r.get("final_score", 0)
            )

            contexts.append(text)

            # TRACK BEST CHUNK
            if score > best_score:
                best_score = score

                best_chunk = {

                    "source":
                        r.get("source", "unknown"),

                    "score":
                        score,

                    "text":
                        text[:300]
                }

        # ONLY SAVE BEST SOURCE
        if best_chunk:
            citations.append(best_chunk)


        # =================================
        # BUILD CONTEXT
        # =================================
       # context = "\n\n".join(contexts)
        context_parts = []

        total = 0

        for r in results:

            txt = r["text"]

            if total + len(txt) > MAX_CONTEXT_CHARS:
                break

            context_parts.append(txt)

            total += len(txt)

        context = "\n\n".join(context_parts)

        best = results[0]["final_score"]

        results = [
            r
            for r in results
            if r["final_score"] >= best * 0.85
        ]

        return context, best


    except Exception as e:

        print("❌ Retrieval Error:", e)

        return "", []


# =================================
# MAIN RAG FUNCTION
# =================================
def answer(question: str):

    # ==========================
    # RETRIEVE
    # ==========================
    results = fusion_search(question)

    if not results:
        return {
            "answer":
                "I don't know based on the documents.",
            "citations": [],
            "context_length": 0
        }

    # ==========================
    # MMR
    # ==========================
    results = apply_mmr(
        results,
        top_k=5,
        lambda_param=0.75
    )

    # ==========================
    # KEEP STRONG RESULTS ONLY
    # ==========================
    best_score = results[0]["final_score"]

    results = [
        r
        for r in results
        if r["final_score"] >= best_score * 0.85
    ]

    # ==========================
    # LIMIT RESULTS
    # ==========================
    results = results[:4]

    # ==========================
    # BUILD CONTEXT
    # ==========================
    context_parts = []

    total_chars = 0

    for r in results:

        txt = r["text"]

        if total_chars + len(txt) > MAX_CONTEXT_CHARS:
            break

        context_parts.append(txt)

        total_chars += len(txt)

    context = "\n\n".join(context_parts)

    # ==========================
    # NO CONTEXT
    # ==========================
    if not context.strip():

        return {
            "answer":
                "I don't know based on the documents.",
            "citations": [],
            "context_length": 0
        }

    # ==========================
    # PROMPT
    # ==========================
    prompt = f"""
Use ONLY the context below to answer the question.

If the answer is not contained in the context,
say:

"I don't know based on the documents."

If code exists in the context,
include the code.

----------------

Context:

{context}

----------------

Question:

{question}

Answer clearly and concisely.
"""

    # ==========================
    # GENERATE
    # ==========================
    answer_text = generate(prompt)

    answer_text = answer_text.strip()

    # ==========================
    # CITATIONS
    # ==========================
    citations = [

        {
            "source":
                r.get("source", "unknown"),

            "filename":
                r.get("filename", "unknown"),

            "score":
                round(
                    r.get("final_score", 0),
                    3
                )
        }

        for r in results[:3]
    ]

    # ==========================
    # RETURN
    # ==========================
    return {

        "answer":
            answer_text,

        "citations":
            citations,

        "context_length":
            len(context)
    }