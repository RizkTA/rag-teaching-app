from llama_index.core.node_parser import SentenceSplitter

splitter = SentenceSplitter(
    chunk_size=800    # ✅ important
    chunk_overlap=80    # ✅ keeps meaning across chunks
)

def chunk_texts(texts):
    chunks = []
    for t in texts:
        chunks.extend(splitter.split_text(t))

    # 🚨 Clean bad chunks
    chunks = [c.strip() for c in chunks if len(c.strip()) > 100]

    return chunks