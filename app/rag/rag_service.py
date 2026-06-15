from app.config import (
    QDRANT_URL,
    QDRANT_COLLECTION,
    EMBED_DIM,
    GROQ_API_KEY
)

from app.vectorstores.qdrant_store import QdrantStore
from app.rag.fusion_rag import fusion_search

from groq import Groq


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

        # USE ONLY TOP 1 CHUNK
        context = contexts[0] if contexts else ""


        # trim context for speed
        context = context[:MAX_CONTEXT_CHARS]


        best_result = results[0] if results else {}

        return context, best_result


    except Exception as e:

        print("❌ Retrieval Error:", e)

        return "", []


# =================================
# MAIN RAG FUNCTION
# =================================
def answer(question: str):

    # =================================
    # RETRIEVE
    # =================================
    #context, best_result  = retrieve(question)

    results = fusion_search(question)
    contexts = [
        r["text"]
        for r in results
    ]
    citations = [
        {
            "source": r["source"],
            "score": r["final_score"],
            "text": r["text"]
        }
        for r in results
    ]

    context = "\n\n".join(contexts)

    # =================================
    # NO CONTEXT
    # =================================
    if not context.strip():

        return {

            "answer":
                "I don't know based on the documents.",

            "citations": [],

            "context_length": 0
        }

    # =================================
    # PROMPT
    # =================================
    prompt = f"""
Use ONLY the context below to answer the question.

If the answer is not contained in the context,
say:
"I don't know based on the documents."

If code exists in the context,
include the code example.

----------------

Context:
{context}

----------------

Question:
{question}

Answer clearly and concisely.
"""

    # =================================
    # GENERATE
    # =================================
    answer_text = generate(prompt)



    # =================================
    # CLEAN COMMON GARBAGE
    # =================================
    answer_text = answer_text.strip()

    # =================================
    # RETURN
    # =================================
    return {

        "answer":
            answer_text,

        "citations":
            citations,

        "context_length":
            len(context)
    }

def rerank_best_source(answer, results):

    answer_words = set(
        answer.lower().split()
    )

    best = None

    best_overlap = -1

    for r in results:

        text = r.get("text", "").lower()

        text_words = set(text.split())

        overlap = len(
            answer_words.intersection(text_words)
        )

        if overlap > best_overlap:

            best_overlap = overlap

            best = r

    return best
