from app.embeddings.local_embedder import LocalEmbedder
from app.teaching.hallucination_detector import detect_hallucination_structured
from fastapi import FastAPI

from app.ingestion.ingest import ingest_pdf
from app.retrieval.retriever import retrieve
from app.llm.olDgenerator import generate_answer

from app.teaching.explainer import explain_rag
from app.teaching.quiz_generator import generate_quiz
from app.teaching.evaluator import evaluate_answer
from app.teaching.visualizer import visualize_retrieval
from fastapi import FastAPI
from vector_db import vector_db
from sklearn.decomposition import PCA
app = FastAPI()

vector_db.add_texts([
    "Artificial Intelligence is transforming education",
    "Machine learning enables predictive systems",
    "RAG combines retrieval with generation"
])

@app.get("/")
def root():
    return {"message": "RAG app is running"}
@app.post("/ingest")
def ingest(path: str):
    return ingest_pdf(path)

@app.post("/query")
def query(payload: dict):
    q = payload.get("q")

    if not q:
        return {"error": "Query is missing"}

    results = vector_db.search(q)

    return {
        "query": q,
        "top_k": len(results),
        "results": results
    }
""""
@app.post("/query")
def query(q: str):

    results = retrieve(q)
    answer = generate_answer(q, results["contexts"])

    return {
        "answer": answer,
        "sources": results["sources"]
    }

"""""
@app.post("/explain")
def explain(q: str):
    return explain_rag(q, retrieve, generate_answer)


@app.post("/quiz")
def quiz(q: str):
    results = retrieve(q)
    quiz = generate_quiz(results["contexts"])
    return {"quiz": quiz}


@app.post("/evaluate")
def evaluate(q: str, student_answer: str):
    results = retrieve(q)
    feedback = evaluate_answer(q, student_answer, results["contexts"])
    return {"evaluation": feedback}


@app.post("/visualize")
def visualize(q: str):
    return visualize_retrieval(q, retrieve)
import traceback

@app.post("/embed_visualize")
def embed_visualize(payload: dict):
    try:
        q = payload.get("q")

        print("DEBUG QUERY:", q)

        # your embedding logic here...

        return {
            "points": points,
            "query": q
        }

    except Exception as e:
        print("ERROR:", str(e))
        traceback.print_exc()
        return {"error": str(e)}
@app.post("/hallucination_structured")
def hallucination_structured(q: str):
    results = retrieve(q)
    answer = generate_answer(q, results["contexts"])
    analysis = detect_hallucination_structured(q, answer, results["contexts"])

    return {
        "answer": answer,
        "analysis": analysis,
        "contexts": results["contexts"]
    }
@app.post("/embed_visualize")
def embed_visualize(payload: dict):
    try:
        q = payload.get("q")

        embeddings, texts = vector_db.get_all_embeddings()

        if len(texts) == 0:
            return {"error": "No data in vector DB"}

        pca = PCA(n_components=2)
        reduced = pca.fit_transform(embeddings)

        points = []
        for i, (x, y) in enumerate(reduced):
            points.append({
                "x": float(x),
                "y": float(y),
                "text": texts[i]
            })

        from vector_db import model
        query_emb = model.encode([q])
        query_reduced = pca.transform(query_emb)[0]

        return {
            "points": points,
            "query": {
                "x": float(query_reduced[0]),
                "y": float(query_reduced[1]),
                "text": q
            }
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": str(e)}
@app.post("/compare_models")
def compare_models(q: str, top_k: int = 5):
    models = {
        "MiniLM": "all-MiniLM-L6-v2",
        "BGE": "BAAI/bge-base-en"
    }

    outputs = {}

    for name, model_name in models.items():
        embedder = LocalEmbedder(model_name)
        # embed query
        q_vec = embedder.embed([q])[0]

        # ⚠️ IMPORTANT:
        # You must use separate collections OR same dimension
        store = QdrantStore(QDRANT_URL, f"{QDRANT_COLLECTION}_{name}", 
                           384 if name == "MiniLM" else 768)

        results = store.search(q_vec, top_k)

        outputs[name] = results

    return outputs