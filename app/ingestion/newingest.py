import os
import uuid

from langchain.text_splitter import RecursiveCharacterTextSplitter
from pypdf import PdfReader

from app.config import (
    QDRANT_URL,
    QDRANT_COLLECTION,
    EMBED_DIM
)

from app.embeddings.api_embedder import embed_texts
from app.vectorstores.qdrant_store import QdrantStore

# =========================================
# INIT QDRANT
# =========================================
store = QdrantStore(
    QDRANT_URL,
    QDRANT_COLLECTION,
    EMBED_DIM
)

# =========================================
# TEXT SPLITTER
# =========================================
splitter = RecursiveCharacterTextSplitter(
    chunk_size=1200,
    chunk_overlap=200
)

# =========================================
# LANGUAGE DETECTOR
# =========================================
def detect_language(filename, text):

    filename = filename.lower()

    # =============================
    # C++
    # =============================
    cpp_extensions = [
        ".cpp",
        ".cc",
        ".cxx",
        ".hpp",
        ".h"
    ]

    if any(filename.endswith(ext) for ext in cpp_extensions):
        return "cpp"

    cpp_keywords = [
        "#include",
        "using namespace std",
        "cout <<",
        "cin >>",
        "int main("
    ]

    if any(k in text for k in cpp_keywords):
        return "cpp"

    # =============================
    # PYTHON
    # =============================
    py_extensions = [
        ".py"
    ]

    if any(filename.endswith(ext) for ext in py_extensions):
        return "python"

    py_keywords = [
        "def ",
        "import ",
        "print(",
        "if __name__ ==",
        "class "
    ]

    if any(k in text for k in py_keywords):
        return "python"

    return "unknown"

# =========================================
# TOPIC DETECTOR
# =========================================
def detect_topic(filepath):

    try:
        return os.path.basename(
            os.path.dirname(filepath)
        )

    except:
        return "general"

# =========================================
# DIFFICULTY DETECTOR
# =========================================
def detect_difficulty(text):

    text = text.lower()

    beginner_keywords = [
        "introduction",
        "basic",
        "simple",
        "beginner"
    ]

    advanced_keywords = [
        "advanced",
        "optimization",
        "dynamic programming",
        "multithreading"
    ]

    if any(k in text for k in beginner_keywords):
        return "beginner"

    if any(k in text for k in advanced_keywords):
        return "advanced"

    return "intermediate"

# =========================================
# READ PDF
# =========================================
def read_pdf(filepath):

    text = ""

    pdf = PdfReader(filepath)

    for page in pdf.pages:

        extracted = page.extract_text()

        if extracted:
            text += extracted + "\n"

    return text

# =========================================
# READ TEXT FILES
# =========================================
def read_text_file(filepath):

    with open(
        filepath,
        "r",
        encoding="utf-8",
        errors="ignore"
    ) as f:

        return f.read()

# =========================================
# MAIN INGEST FUNCTION
# =========================================
def ingest_file(filepath):

    filename = os.path.basename(filepath)

    print(f"📄 Ingesting: {filename}")

    # =====================================
    # READ FILE
    # =====================================
    if filename.lower().endswith(".pdf"):

        text = read_pdf(filepath)

    else:

        text = read_text_file(filepath)

    if not text.strip():

        print("⚠️ Empty file")
        return

    # =====================================
    # DETECT METADATA
    # =====================================
    language = detect_language(
        filename,
        text
    )

    topic = detect_topic(filepath)

    difficulty = detect_difficulty(text)

    print(f"🧠 Language: {language}")
    print(f"📚 Topic: {topic}")
    print(f"🎯 Difficulty: {difficulty}")

    # =====================================
    # SPLIT INTO CHUNKS
    # =====================================
    chunks = splitter.split_text(text)

    print(f"✂️ Chunks: {len(chunks)}")

    # =====================================
    # EMBEDDINGS
    # =====================================
    vectors = embed_texts(chunks)

    ids = []
    payloads = []

    # =====================================
    # BUILD PAYLOADS
    # =====================================
    for i, chunk in enumerate(chunks):

        ids.append(str(uuid.uuid4()))

        payload = {
            "text": chunk,
            "source": filename,
            "chunk_id": i,
            "topic": topic,
            "language": language,
            "difficulty": difficulty
        }

        payloads.append(payload)

    # =====================================
    # UPSERT TO QDRANT
    # =====================================
    store.upsert(
        ids=ids,
        vectors=vectors,
        payloads=payloads
    )

    print("✅ Ingestion complete")

# =========================================
# INGEST ENTIRE FOLDER
# =========================================
def ingest_folder(folder="docs"):

    supported_extensions = [
        ".pdf",
        ".md",
        ".txt",
        ".cpp",
        ".cc",
        ".cxx",
        ".hpp",
        ".h",
        ".py"
    ]

    for root, dirs, files in os.walk(folder):

        for file in files:

            if any(
                file.lower().endswith(ext)
                for ext in supported_extensions
            ):

                filepath = os.path.join(
                    root,
                    file
                )

                try:

                    ingest_file(filepath)

                except Exception as e:

                    print(
                        f"❌ Failed: {file}"
                    )

                    print(str(e))

# =========================================
# MAIN
# =========================================
if __name__ == "__main__":

    ingest_folder("docs")